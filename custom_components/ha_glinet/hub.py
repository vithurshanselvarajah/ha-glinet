from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, TypeVar

from aiohttp import ClientError
from homeassistant.components.device_tracker import (
    CONF_CONSIDER_HOME,
    DEFAULT_CONSIDER_HOME,
)
from homeassistant.components.device_tracker import (
    DOMAIN as TRACKER_DOMAIN,
)
from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_USERNAME,
)
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC, format_mac
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    APIClientError,
    GLinetApiClient,
    NonZeroResponse,
    TailscaleConnection,
    TokenError,
)
from .api.exceptions import AuthenticationError
from .api.models import RouterStatus
from .const import (
    API_PATH,
    CONF_ADD_ALL_DEVICES,
    CONF_ENABLED_FEATURES,
    DEFAULT_USERNAME,
    DOMAIN,
    FEATURE_CELLULAR,
    FEATURE_OPTIONS,
    FEATURE_OVPN_CLIENT,
    FEATURE_OVPN_SERVER,
    FEATURE_REPEATER,
    FEATURE_SMS,
    FEATURE_TAILSCALE,
    FEATURE_WG_CLIENT,
    FEATURE_WG_SERVER,
    FEATURE_ZEROTIER,
)
from .models import (
    ClientDeviceInfo,
    FanStatus,
    OpenVpnClient,
    OpenVpnServerStatus,
    RepeaterState,
    RepeaterStatus,
    ScannedNetwork,
    SmsMessage,
    WifiInterface,
    WireGuardClient,
    WireGuardServerStatus,
    ZeroTierStatus,
)
from .utils import compute_mac_offset, get_first_int

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_registry import RegistryEntry

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=30)
T = TypeVar("T")


class GLinetHub(DataUpdateCoordinator[None]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self._entry = entry
        self._options = dict(entry.options)
        self._settings = dict(entry.data) | dict(entry.options)
        self._host: str = self._settings[CONF_HOST]
        self._api: GLinetApiClient | None = None

        self._factory_mac = "UNKNOWN"
        self._model = "UNKNOWN"
        self._sw_version = "UNKNOWN"

        self._devices: dict[str, ClientDeviceInfo] = {}
        self._wifi_ifaces: dict[str, WifiInterface] = {}
        self._system_status: RouterStatus | None = None
        self._cellular_status: dict[str, Any] = {}
        self._modems: dict[str, dict[str, Any]] = {}
        self._cached_modem_info: dict[str, Any] | None = None
        self._default_modem_bus: str | None = None
        self._wireguard_clients: dict[int, WireGuardClient] = {}
        self._wireguard_connections: list[WireGuardClient] | None = None
        self._tailscale_config: dict[str, Any] = {}
        self._tailscale_connection: bool | None = None
        self._sms_messages: dict[str, SmsMessage] = {}
        self._repeater_status: RepeaterStatus | None = None
        self._repeater_config: dict[str, Any] = {}
        self._scanned_networks: list[ScannedNetwork] = []
        self._last_wifi_scan: datetime | None = None
        self._saved_networks: list[dict[str, Any]] = []
        self._fan_status: FanStatus | None = None
        self._wg_server_peers: list[dict[str, Any]] = []
        self._ovpn_clients: dict[str, OpenVpnClient] = {}
        self._ovpn_connections: list[OpenVpnClient] | None = None
        self._ovpn_server_status: dict[str, Any] = {}
        self._ovpn_server_users: list[dict[str, Any]] = []
        self._ovpn_raw_clients: dict[str, dict[str, Any]] = {}
        self._ovpn_client_status: dict[str, Any] = {}
        self._zerotier_status: ZeroTierStatus | None = None

        self._late_init_complete = False
        self._connect_error = False
        self._token_error = False

    async def _async_update_data(self) -> None:
        """Fetch data from GL-INet router."""
        try:
            await self.fetch_all_data()
        except ConfigEntryAuthFailed:
            raise
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    @property
    def enabled_features(self) -> set[str]:
        return set(self._settings.get(CONF_ENABLED_FEATURES, FEATURE_OPTIONS))

    def feature_enabled(self, feature: str) -> bool:
        return feature in self.enabled_features

    async def async_initialize_hub(self) -> None:
        if not self._late_init_complete:
            await self._async_load_router_info()

        entity_registry = er.async_get(self.hass)
        track_entries: list[RegistryEntry] = er.async_entries_for_config_entry(
            entity_registry, self._entry.entry_id
        )

        feature_map = {
            FEATURE_CELLULAR: ["cellular_"],
            FEATURE_SMS: ["sms_messages", "text_messages"],
            FEATURE_REPEATER: [
                "repeater_",
                "wifi_network",
                "scan_wifi",
                "disconnect_repeater",
            ],
            FEATURE_TAILSCALE: ["tailscale"],
            FEATURE_WG_CLIENT: [
                "wireguard_client",
                "vpn_client",
                "wg_client",
            ],
            FEATURE_WG_SERVER: [
                "wg_server",
            ],
            FEATURE_OVPN_CLIENT: [
                "ovpn_client",
            ],
            FEATURE_OVPN_SERVER: [
                "ovpn_server",
            ],
        }

        for entry in track_entries:
            removed = False
            for feature, keywords in feature_map.items():
                if not self.feature_enabled(feature):
                    if any(k in entry.unique_id for k in keywords):
                        _LOGGER.debug(
                            "Removing orphan entity %s (feature %s disabled)",
                            entry.entity_id,
                            feature,
                        )
                        entity_registry.async_remove(entry.entity_id)
                        removed = True
                        break

            if not removed and not self._settings.get(CONF_ADD_ALL_DEVICES):
                mac = None
                if entry.domain == TRACKER_DOMAIN:
                    mac = entry.unique_id
                elif entry.unique_id.startswith("glinet_client_sensor/"):
                    mac = entry.unique_id.split("/")[1]

                if mac:
                    dev_reg = dr.async_get(self.hass)
                    device = dev_reg.async_get_device(
                        connections={(CONNECTION_NETWORK_MAC, format_mac(mac))}
                    )
                    if not device or not any(
                        eid != self._entry.entry_id for eid in device.config_entries
                    ):
                        _LOGGER.debug(
                            "Removing unknown device entity %s (discovery disabled)",
                            entry.entity_id,
                        )
                        entity_registry.async_remove(entry.entity_id)
                        if device:
                            _LOGGER.debug(
                                "Removing unknown device %s (discovery disabled)",
                                device.name or mac,
                            )
                            dev_reg.async_remove_device(device.id)
                        removed = True

            if removed:
                continue

            if entry.domain == TRACKER_DOMAIN:
                self._devices[entry.unique_id] = ClientDeviceInfo(
                    entry.unique_id,
                    entry.original_name,
                )
        await self.fetch_all_data()

    def _create_api_client(self) -> GLinetApiClient:
        session = async_get_clientsession(self.hass)
        return GLinetApiClient(base_url=f"{self._host}{API_PATH}", session=session)

    async def _async_load_router_info(self) -> None:
        try:
            self._api = self._create_api_client()
            await self._api.authenticate(
                self._settings.get(CONF_USERNAME, DEFAULT_USERNAME),
                self._settings[CONF_PASSWORD],
            )
            router_info = await self._invoke_api(self._api.system.get_info)
        except (ClientError, TimeoutError, OSError) as exc:
            _LOGGER.exception("Error connecting to GL-INet router %s", self._host)
            raise ConfigEntryNotReady from exc
        except AuthenticationError as exc:
            raise ConfigEntryAuthFailed from exc

        if not router_info:
            raise ConfigEntryNotReady("Unable to retrieve router info during setup")

        self._model = str(router_info.model or "UNKNOWN")
        self._sw_version = str(router_info.firmware_version or "UNKNOWN")
        self._factory_mac = str(router_info.mac or "UNKNOWN")
        self._late_init_complete = True

    async def refresh_session_token(self) -> None:
        api = self.router_api
        attempts = 3
        for attempt in range(attempts):
            try:
                await api.authenticate(
                    self._settings.get(CONF_USERNAME, DEFAULT_USERNAME),
                    self._settings[CONF_PASSWORD],
                )
                _LOGGER.debug("GL-INet router %s token was renewed", self._host)
                return
            except (AuthenticationError, TokenError, NonZeroResponse) as exc:
                if attempt < attempts - 1:
                    _LOGGER.debug(
                        "Attempt %d/%d: GL-INet router %s failed to renew token: %s. Retrying...",
                        attempt + 1,
                        attempts,
                        self._host,
                        exc,
                    )
                    continue
                _LOGGER.error(
                    "GL-INet router %s failed to renew the token after %d attempts: %s.",
                    self._host,
                    attempts,
                    exc,
                )
                raise ConfigEntryAuthFailed from exc

    async def fetch_all_data(self, _: datetime | None = None) -> None:
        try:
            await self.refresh_session_token()
        except ConfigEntryAuthFailed:
            raise
        except (APIClientError, ClientError, TimeoutError, OSError):
            _LOGGER.debug(
                "Proactive token refresh failed for %s; will retry during API calls",
                self._host,
            )

        tasks: list[Awaitable[Any]] = [
            self.fetch_system_status(),
            self.fetch_connected_devices(),
            self.fetch_wifi_interfaces(),
            self.fetch_fan_status(),
        ]

        if self.feature_enabled(FEATURE_WG_CLIENT):
            tasks.append(self.fetch_wireguard_clients())
        else:
            self._wireguard_clients = {}
            self._wireguard_connections = None

        if self.feature_enabled(FEATURE_WG_SERVER):
            tasks.append(self.fetch_wg_server_status())
        else:
            self._wg_server_status = {}
            self._wg_server_peers = []

        if self.feature_enabled(FEATURE_OVPN_CLIENT):
            tasks.append(self.fetch_ovpn_clients())
        else:
            self._ovpn_clients = {}
            self._ovpn_connections = None

        if self.feature_enabled(FEATURE_OVPN_SERVER):
            tasks.append(self.fetch_ovpn_server_status())
        else:
            self._ovpn_server_status = {}
            self._ovpn_server_users = []

        if self.feature_enabled(FEATURE_TAILSCALE):
            tasks.append(self.fetch_tailscale_state())
        else:
            self._tailscale_config = {}
            self._tailscale_connection = None

        if self.feature_enabled(FEATURE_ZEROTIER):
            tasks.append(self.fetch_zerotier_status())
        else:
            self._zerotier_status = None

        if self.feature_enabled(FEATURE_CELLULAR):
            tasks.append(self.fetch_cellular_status())
        else:
            self._cellular_status = {}
            self._modems = {}
            self._cached_modem_info = None
            self._default_modem_bus = None

        if self.feature_enabled(FEATURE_REPEATER):
            tasks.extend(
                [
                    self.fetch_repeater_status(),
                    self.fetch_repeater_config(),
                    self.fetch_saved_networks(),
                ]
            )
        else:
            self._repeater_status = None
            self._repeater_config = {}
            self._scanned_networks = []
            self._saved_networks = []
            self._last_wifi_scan = None

        for task in tasks:
            await task

        if self.feature_enabled(FEATURE_SMS):
            await self.fetch_sms_messages()
        else:
            self._sms_messages = {}

    async def _async_poll_update(self, _: datetime | None = None) -> None:
        await self.async_refresh()

    async def _invoke_api(self, api_callable: Callable[[], Awaitable[T]]) -> T | None:
        try:
            if self._token_error or self._connect_error:
                await self.refresh_session_token()
            response = await api_callable()
        except TimeoutError:
            if not self._connect_error:
                _LOGGER.exception("GL-INet router %s did not respond in time", self._host)
            self._connect_error = True
            return None
        except (TokenError, AuthenticationError):
            if not self._connect_error:
                _LOGGER.warning(
                    "GL-INet router %s rejected the token or access was denied; "
                    "a reauthentication will be attempted",
                    self._host,
                )
            self._connect_error = True
            self._token_error = True
            return None
        except NonZeroResponse:
            if not self._connect_error:
                _LOGGER.exception("GL-INet router %s returned a router error response", self._host)
            self._connect_error = True
            return None
        except ConfigEntryAuthFailed:
            raise
        except Exception:
            if not self._connect_error:
                _LOGGER.exception("GL-INet router %s returned an unexpected error", self._host)
            self._connect_error = True
            return None

        if self._token_error:
            self._token_error = False
            _LOGGER.info("GL-INet router %s token is valid again", self._host)
        if self._connect_error:
            self._connect_error = False
            _LOGGER.info("Reconnected to GL-INet router %s", self._host)
        return response

    async def _invoke_optional_api(self, api_callable: Callable[[], Awaitable[T]]) -> T | None:
        try:
            return await api_callable()
        except (TokenError, AuthenticationError):
            self._token_error = True
            return None
        except (APIClientError, OSError, TimeoutError, ValueError, NonZeroResponse):
            _LOGGER.debug("Optional GL-INet router API is unavailable", exc_info=True)
            return None

    async def fetch_system_status(self) -> None:
        response = await self._invoke_api(self.router_api.system.get_status)
        if response:
            self._system_status = response

    async def reboot(self, delay: int = 0) -> None:
        await self._invoke_api(lambda: self.router_api.system.reboot(delay))


    async def fetch_connected_devices(self) -> None:
        new_device = False
        connected_devices = await self._invoke_api(self.router_api.clients.get_online)
        if connected_devices is None:
            return

        consider_home = self._options.get(CONF_CONSIDER_HOME, DEFAULT_CONSIDER_HOME.total_seconds())
        for device_mac, device in self._devices.items():
            device.apply_update(connected_devices.get(device_mac), consider_home)

        dev_reg = dr.async_get(self.hass)
        for device_mac, dev_info in connected_devices.items():
            if device_mac in self._devices:
                continue

            existing_device = dev_reg.async_get_device(
                connections={(CONNECTION_NETWORK_MAC, format_mac(device_mac))}
            )

            if not existing_device or not any(
                entry_id != self._entry.entry_id for entry_id in existing_device.config_entries
            ):
                if not self._settings.get(CONF_ADD_ALL_DEVICES):
                    continue
                device_is_known = False
            else:
                device_is_known = True

            new_device = True
            device = ClientDeviceInfo(device_mac)
            device.is_known = device_is_known
            device.apply_update(dev_info)
            self._devices[device_mac] = device

        async_dispatcher_send(self.hass, self.event_device_updated)
        if new_device:
            async_dispatcher_send(self.hass, self.event_device_added)

    async def fetch_wifi_interfaces(self) -> None:
        response = await self._invoke_api(self.router_api.wifi.get_interfaces)
        if not response:
            return
        for name, iface in response.items():
            self._wifi_ifaces[name] = WifiInterface(
                name=name,
                enabled=iface.enabled,
                ssid=iface.ssid,
                guest=iface.guest,
                hidden=iface.hidden,
                encryption=iface.encryption or "UNKNOWN",
            )

    async def set_wifi_interface_enabled(self, iface_name: str, enabled: bool) -> None:
        await self._invoke_api(
            lambda: self.router_api.wifi.set_interface_enabled(iface_name, enabled)
        )
        await self.fetch_wifi_interfaces()

    async def fetch_wireguard_clients(self) -> None:
        response = await self._invoke_api(self.router_api.wg_client.get_wireguard_clients)
        if response is None:
            return

        self._wireguard_clients = {
            int(config["peer_id"]): WireGuardClient(
                name=str(config["name"]),
                connected=False,
                group_id=int(config["group_id"]),
                peer_id=int(config["peer_id"]),
                tunnel_id=(
                    int(config["tunnel_id"])
                    if config.get("tunnel_id") is not None
                    else None
                ),
            )
            for config in response
        }
        if not self._wireguard_clients:
            self._wireguard_connections = []
            return

        state_response = await self._invoke_api(self.router_api.wg_client.get_wireguard_state)
        if state_response is None:
            return

        self._wireguard_connections = []
        for config in state_response:
            if config.get("type") not in {None, "wireguard"}:
                continue
            peer_id = config.get("peer_id")
            if peer_id not in self._wireguard_clients:
                continue
            client = self._wireguard_clients[peer_id]
            client.tunnel_id = config.get("tunnel_id", client.tunnel_id)
            client.connected = config.get("status", 0) != 0 or bool(config.get("enabled", False))
            if client.connected:
                self._wireguard_connections.append(client)

    async def start_vpn_client(self, group_id: int, peer_id: int) -> None:
        await self._invoke_api(
            lambda: self.router_api.wg_client.start_wireguard_client(group_id, peer_id)
        )
        await self.fetch_wireguard_clients()

    async def stop_vpn_client(self, peer_id: int) -> None:
        await self._invoke_api(
            lambda: self.router_api.wg_client.stop_wireguard_client(peer_id)
        )
        await self.fetch_wireguard_clients()

    async def fetch_wg_server_status(self) -> None:
        response = await self._invoke_api(self.router_api.wg_server.get_status)
        if response is None:
            self._wg_server_status = {}
            return
        self._wg_server_status = response
        self._wg_server_peers = response.get("peers") or []

    async def start_wg_server(self) -> None:
        await self._invoke_api(self.router_api.wg_server.start)
        await self.fetch_wg_server_status()

    async def stop_wg_server(self) -> None:
        await self._invoke_api(self.router_api.wg_server.stop)
        await self.fetch_wg_server_status()

    async def fetch_ovpn_clients(self) -> None:
        response = await self._invoke_api(self.router_api.ovpn_client.get_ovpn_clients)
        if response is None:
            return

        self._ovpn_clients = {}
        self._ovpn_raw_clients = {}
        for config in response:
            key = f"{config['group_id']}_{config['client_id']}"
            locations = []
            if config.get("location"):
                locations = [loc.strip() for loc in config["location"].split(";")]
            
            remotes = []
            remote_val = config.get("remote")
            if isinstance(remote_val, list):
                remotes = remote_val
            elif isinstance(remote_val, str):
                remotes = [remote_val]

            self._ovpn_clients[key] = OpenVpnClient(
                name=str(config["name"]),
                connected=False,
                group_id=int(config["group_id"]),
                client_id=int(config["client_id"]),
                group_name=config.get("group_name"),
                location=config.get("location"),
                locations=locations,
                remotes=remotes,
            )
            self._ovpn_raw_clients[key] = config["raw_data"]

        if not self._ovpn_clients:
            self._ovpn_connections = []
            return

        state_response = await self._invoke_api(self.router_api.ovpn_client.get_status)
        if state_response is None:
            self._ovpn_client_status = {}
            return

        self._ovpn_client_status = state_response
        self._ovpn_connections = []
        status = state_response.get("status", 0)
        if status != 0:
            gid = state_response.get("group_id")
            cid = state_response.get("client_id")
            key = f"{gid}_{cid}"
            if key in self._ovpn_clients:
                client = self._ovpn_clients[key]
                client.connected = True
                self._ovpn_connections.append(client)

    async def set_ovpn_client_location(
        self, group_id: int, client_id: int, location_index: int
    ) -> None:
        key = f"{group_id}_{client_id}"
        if key not in self._ovpn_raw_clients:
            return
        
        client = self._ovpn_clients[key]
        if location_index >= len(client.remotes):
            return
        
        selected_remote = client.remotes[location_index]
        
        params = dict(self._ovpn_raw_clients[key])
        params["group_id"] = group_id
        params["client_id"] = client_id
        params["remote"] = selected_remote
        
        params.pop("location", None)
        
        await self._invoke_api(lambda: self.router_api.ovpn_client.set_config(params))
        
        if client.connected:
            await self.stop_ovpn_client()
            await self.start_ovpn_client(group_id, client_id)
        else:
            await self.fetch_ovpn_clients()

    @property
    def ovpn_client_status(self) -> dict[str, Any]:
        return self._ovpn_client_status

    async def start_ovpn_client(self, group_id: int, client_id: int) -> None:
        await self._invoke_api(
            lambda: self.router_api.ovpn_client.start(group_id, client_id)
        )
        await self.fetch_ovpn_clients()

    async def stop_ovpn_client(self) -> None:
        await self._invoke_api(self.router_api.ovpn_client.stop)
        await self.fetch_ovpn_clients()

    async def fetch_ovpn_server_status(self) -> None:
        status_response = await self._invoke_api(self.router_api.ovpn_server.get_status)
        if status_response is None:
            self._ovpn_server_status = {}
            return
        self._ovpn_server_status = status_response
        
        users_response = await self._invoke_api(self.router_api.ovpn_server.get_user_list)
        self._ovpn_server_users = users_response or []

    async def start_ovpn_server(self) -> None:
        await self._invoke_api(self.router_api.ovpn_server.start)
        await self.fetch_ovpn_server_status()

    async def stop_ovpn_server(self) -> None:
        await self._invoke_api(self.router_api.ovpn_server.stop)
        await self.fetch_ovpn_server_status()

    async def fetch_tailscale_state(self) -> None:
        details = await self._invoke_optional_api(self.router_api.tailscale.get_details)
        if not details:
            self._tailscale_config = {}
            self._tailscale_connection = None
            return

        self._tailscale_config = details["config"]
        self._tailscale_connection = details["connection"] == TailscaleConnection.CONNECTED

    async def connect_tailscale(self) -> None:
        await self._invoke_api(self.router_api.tailscale.connect)
        await self.fetch_tailscale_state()

    async def disconnect_tailscale(self) -> None:
        await self._invoke_api(self.router_api.tailscale.disconnect)
        await self.fetch_tailscale_state()

    @property
    def zerotier_status(self) -> ZeroTierStatus | None:
        return self._zerotier_status

    async def fetch_zerotier_status(self) -> None:
        config = await self._invoke_optional_api(self.router_api.zerotier.get_config)
        status = await self._invoke_optional_api(self.router_api.zerotier.get_status)
        if config is None or status is None:
            self._zerotier_status = None
            return
        self._zerotier_status = ZeroTierStatus.from_api_response(config, status)

    async def start_zerotier(self) -> None:
        if self._zerotier_status and self._zerotier_status.network_id:
            await self._invoke_api(
                lambda: self.router_api.zerotier.set_config(
                    {"enabled": True, "id": self._zerotier_status.network_id}
                )
            )
            await self.fetch_zerotier_status()

    async def stop_zerotier(self) -> None:
        if self._zerotier_status and self._zerotier_status.network_id:
            await self._invoke_api(
                lambda: self.router_api.zerotier.set_config(
                    {"enabled": False, "id": self._zerotier_status.network_id}
                )
            )
            await self.fetch_zerotier_status()

    async def fetch_cellular_status(self) -> None:
        if self._cached_modem_info is None:
            info_response = await self._invoke_optional_api(self.router_api.modem.get_info)
            self._cached_modem_info = dict(info_response or {})
        else:
            info_response = self._cached_modem_info

        status_response = await self._invoke_optional_api(self.router_api.modem.get_status)

        modems = _merge_modem_lists(
            dict(info_response or {}).get("modems", []),
            dict(status_response or {}).get("modems", []),
        )
        self._modems = {
            str(modem["bus"]): modem
            for modem in modems
            if modem.get("bus")
        }
        self._default_modem_bus = _select_sms_modem_bus(self._modems)
        self._cellular_status = {
            "modems": modems,
            "default_bus": self._default_modem_bus,
        }

    async def fetch_repeater_status(self) -> None:
        response = await self._invoke_optional_api(self.router_api.repeater.get_status)
        if response is None:
            self._repeater_status = None
            return
        self._repeater_status = RepeaterStatus.from_api_response(response)

    async def fetch_repeater_config(self) -> None:
        response = await self._invoke_optional_api(self.router_api.repeater.get_config)
        if response is not None:
            self._repeater_config = response

    async def set_repeater_auto_switch(self, enabled: bool) -> None:
        await self._invoke_api(
            lambda: self.router_api.repeater.set_config({"auto": enabled})
        )
        await self.fetch_repeater_config()

    async def set_repeater_band(self, band: str | None) -> None:
        await self._invoke_api(
            lambda: self.router_api.repeater.set_config({"lock_band": band})
        )
        await self.fetch_repeater_config()

    async def fetch_fan_status(self) -> None:
        status = await self._invoke_optional_api(self.router_api.fan.get_status)
        if status is None:
            self._fan_status = None
            return
        config = await self._invoke_optional_api(self.router_api.fan.get_config)
        self._fan_status = FanStatus.from_api_response(status, config or {})

    async def set_fan_temperature(self, temperature: int) -> None:
        await self._invoke_api(lambda: self.router_api.fan.set_config(temperature))
        await self.fetch_fan_status()

    async def test_fan(self, duration: int = 10) -> None:
        await self._invoke_api(lambda: self.router_api.fan.set_test(test=True, time=duration))

    async def scan_wifi_networks(
        self, all_band: bool = False, dfs: bool = False, store_results: bool = True
    ) -> list[ScannedNetwork]:
        _LOGGER.info("Starting WiFi network scan (all_band=%s, dfs=%s)", all_band, dfs)
        response = await self._invoke_api(
            lambda: self.router_api.repeater.scan({"all_band": all_band, "dfs": dfs})
        )
        if response is None:
            _LOGGER.warning(
                "WiFi scan returned None, keeping %d cached networks",
                len(self._scanned_networks),
            )
            return self._scanned_networks
        networks = [ScannedNetwork.from_api_response(network) for network in response]
        _LOGGER.info("WiFi scan found %d networks", len(networks))
        if store_results:
            self._scanned_networks = networks
            self._last_wifi_scan = datetime.now()
            async_dispatcher_send(self.hass, self.event_networks_updated)
        return networks

    async def connect_to_wifi(
        self,
        ssid: str,
        password: str | None = None,
        remember: bool = True,
        bssid: str | None = None,
    ) -> None:
        await self._invoke_api(
            lambda: self.router_api.repeater.connect(
                {"ssid": ssid, "key": password, "remember": remember, "bssid": bssid}
            )
        )
        await self.fetch_repeater_status()

    async def disconnect_wifi(self) -> None:
        await self._invoke_api(self.router_api.repeater.disconnect)
        await self.fetch_repeater_status()

    async def fetch_saved_networks(self) -> None:
        response = await self._invoke_optional_api(self.router_api.repeater.get_saved_ap_list)
        if response is not None:
            self._saved_networks = response

    async def get_saved_wifi_networks(self) -> list[dict[str, Any]]:
        response = await self._invoke_api(self.router_api.repeater.get_saved_ap_list)
        return response or []

    async def remove_saved_wifi_network(self, ssid: str) -> None:
        await self._invoke_api(lambda: self.router_api.repeater.remove_saved_ap(ssid))
        await self.fetch_saved_networks()

    async def fetch_sms_messages(self) -> None:
        response = await self._invoke_optional_api(self.router_api.modem.get_sms_list)
        if response is None:
            return
        messages: dict[str, SmsMessage] = {}
        for index, item in enumerate(response):
            message_id = str(
                item.get("name")
                or item.get("id")
                or item.get("index")
                or item.get("message_id")
                or item.get("sn")
                or index
            )
            messages[message_id] = SmsMessage(
                message_id=message_id,
                phone_number=str(item.get("phone_number") or item.get("sender") or ""),
                text=str(item.get("body") or ""),
                bus=item.get("bus"),
                status=get_first_int(item, ("status",)),
                timestamp=item.get("date") or item.get("time") or item.get("timestamp"),
                read=_sms_status_is_read(item.get("status")),
            )
        self._sms_messages = messages

    async def send_sms(self, recipient: str, text: str) -> None:
        bus = self._default_modem_bus
        if bus is None:
            await self.fetch_cellular_status()
            bus = self._default_modem_bus
        if bus is None:
            raise RuntimeError("No SMS-capable GL-INet modem was found")

        chunks = [text[i : i + 160] for i in range(0, len(text), 160)]
        for chunk in chunks:
            response = await self._invoke_optional_api(
                lambda c=chunk: self.router_api.modem.send_sms(bus, recipient, c)
            )
            if response is None:
                raise RuntimeError("The router did not accept the SMS send request")

        await self.fetch_sms_messages()

    async def remove_sms(
        self, scope: int, message_id: str | None = None
    ) -> None:
        message = self._sms_messages.get(message_id) if message_id else None
        bus = message.bus if message else self._default_modem_bus

        if bus is None:
            await self.fetch_cellular_status()
            bus = self._default_modem_bus
        if bus is None:
            raise RuntimeError("No GL-INet modem bus is available for SMS removal")

        await self._invoke_optional_api(
            lambda: self.router_api.modem.remove_sms(bus, scope, message_id)
        )
        if scope == 10 and message_id:
            self._sms_messages.pop(message_id, None)
        else:
            await self.fetch_sms_messages()

    def apply_option_updates(self, new_options: dict[str, Any]) -> bool:
        self._options.update(new_options)
        self._settings = dict(self._entry.data) | new_options
        return True

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.router_id)},
            connections={
                (CONNECTION_NETWORK_MAC, format_mac(self.device_mac)),
                (CONNECTION_NETWORK_MAC, compute_mac_offset(self.device_mac, 1)),
            },
            name=self.hub_name,
            model=self.router_model or "GL-INet Router",
            manufacturer="GL-INet",
            configuration_url=self._host,
            sw_version=self._sw_version,
        )

    @property
    def router_api(self) -> GLinetApiClient:
        if self._api is None:
            raise RuntimeError("GL-INet API client has not been initialized")
        return self._api

    @property
    def router_host(self) -> str:
        return self._host

    @property
    def router_id(self) -> str:
        return self._entry.unique_id or self._entry.entry_id

    @property
    def device_mac(self) -> str:
        return self._factory_mac

    @property
    def router_model(self) -> str:
        return self._model.upper()

    @property
    def hub_name(self) -> str:
        return f"GL-INet {self._model.upper()}"

    @property
    def tracked_devices(self) -> dict[str, ClientDeviceInfo]:
        return self._devices

    @property
    def wifi_interfaces(self) -> dict[str, WifiInterface]:
        return self._wifi_ifaces

    @property
    def vpn_clients(self) -> dict[int, WireGuardClient]:
        return self._wireguard_clients

    @property
    def connected_vpn_clients(self) -> list[WireGuardClient] | None:
        return self._wireguard_connections

    @property
    def wg_server_status(self) -> WireGuardServerStatus | None:
        if not self._wg_server_status:
            return None
        return WireGuardServerStatus.from_api_response(self._wg_server_status)

    @property
    def wg_server_connected_users(self) -> int:
        if not self._wg_server_peers:
            return 0
        return sum(1 for p in self._wg_server_peers if p.get("status") == 1)

    @property
    def ovpn_clients(self) -> dict[str, OpenVpnClient]:
        return self._ovpn_clients

    @property
    def connected_ovpn_clients(self) -> list[OpenVpnClient] | None:
        return self._ovpn_connections

    @property
    def ovpn_server_status(self) -> OpenVpnServerStatus | None:
        if not self._ovpn_server_status:
            return None
        return OpenVpnServerStatus.from_api_response(
            self._ovpn_server_status, self._ovpn_server_users
        )

    @property
    def ovpn_server_connected_users(self) -> int:
        return len(self._ovpn_server_users)

    @property
    def router_status(self) -> RouterStatus | None:
        return self._system_status


    @property
    def cellular_status(self) -> dict[str, Any]:
        return self._cellular_status

    @property
    def online_client_count(self) -> int:
        return sum(1 for device in self._devices.values() if device.is_connected)

    @property
    def has_tailscale(self) -> bool:
        return bool(self._tailscale_config)

    @property
    def tailscale_settings(self) -> dict[str, Any]:
        return self._tailscale_config

    @property
    def tailscale_connected(self) -> bool | None:
        return self._tailscale_connection

    @property
    def has_zerotier(self) -> bool:
        return self._zerotier_status is not None

    @property
    def zerotier_connected(self) -> bool | None:
        if self._zerotier_status is None:
            return None
        return self._zerotier_status.connected

    @property
    def sms_messages(self) -> dict[str, SmsMessage]:
        return self._sms_messages

    @property
    def default_modem_bus(self) -> str | None:
        return self._default_modem_bus

    @property
    def repeater_status(self) -> RepeaterStatus | None:
        return self._repeater_status

    @property
    def repeater_connected(self) -> bool | None:
        if self._repeater_status is None:
            return None
        return self._repeater_status.state == RepeaterState.CONNECTED

    @property
    def repeater_config(self) -> dict[str, Any]:
        return self._repeater_config

    @property
    def repeater_auto_switch(self) -> bool | None:
        return self._repeater_config.get("auto")

    @property
    def repeater_band(self) -> str | None:
        return self._repeater_config.get("lock_band")

    @property
    def scanned_networks(self) -> list[ScannedNetwork]:
        return self._scanned_networks

    @property
    def saved_networks(self) -> list[dict[str, Any]]:
        return self._saved_networks

    @property
    def last_wifi_scan(self) -> datetime | None:
        return self._last_wifi_scan

    @property
    def fan_status(self) -> FanStatus | None:
        return self._fan_status

    @property
    def fan_running(self) -> bool | None:
        if self._fan_status is None:
            return None
        return self._fan_status.running

    @property
    def fan_speed(self) -> int | None:
        if self._fan_status is None:
            return None
        if not self._fan_status.running:
            return 0
        return self._fan_status.speed

    @property
    def fan_temperature_threshold(self) -> int | None:
        if self._fan_status is None:
            return None
        return self._fan_status.temperature_threshold

    @property
    def event_device_added(self) -> str:
        return f"{DOMAIN}-device-new-{self._factory_mac}"

    @property
    def event_device_updated(self) -> str:
        return f"{DOMAIN}-device-update-{self._factory_mac}"

    @property
    def event_networks_updated(self) -> str:
        return f"{DOMAIN}-networks-update-{self._factory_mac}"

def _merge_modem_lists(
    info_modems: list[dict[str, Any]],
    status_modems: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for modem in [*info_modems, *status_modems]:
        if not isinstance(modem, dict) or not modem.get("bus"):
            continue
        bus = str(modem["bus"])
        merged[bus] = merged.get(bus, {}) | dict(modem)
    return list(merged.values())


def _select_sms_modem_bus(modems: dict[str, dict[str, Any]]) -> str | None:
    for bus, modem in modems.items():
        if modem.get("sms_support") is True:
            return bus
    for bus, modem in modems.items():
        if modem.get("simcard"):
            return bus
    return next(iter(modems), None)


def _sms_status_is_read(status: Any) -> bool | None:
    if status == 0:
        return False
    if isinstance(status, int):
        return status in {1, 2, 3, 4, 5}
    return None
