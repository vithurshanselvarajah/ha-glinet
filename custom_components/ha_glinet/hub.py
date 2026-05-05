from __future__ import annotations

import asyncio
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
    CONF_MAC,
    CONF_MODEL,
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
from homeassistant.helpers.event import async_track_time_interval

from .api import (
    APIClientError,
    GLinetApiClient,
    NonZeroResponse,
    TailscaleConnection,
    TokenError,
)
from .api.exceptions import AuthenticationError
from .const import API_PATH, DEFAULT_USERNAME, DOMAIN
from .models import ClientDeviceInfo, SmsMessage, WifiInterface, WireGuardClient
from .utils import compute_mac_offset

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_registry import RegistryEntry

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=30)
T = TypeVar("T")


class GLinetHub:
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
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
        self._system_status: dict[str, Any] = {}
        self._internet_status: dict[str, Any] = {}
        self._cellular_status: dict[str, Any] = {}
        self._modems: dict[str, dict[str, Any]] = {}
        self._cached_modem_info: dict[str, Any] | None = None
        self._default_modem_bus: str | None = None
        self._wireguard_clients: dict[int, WireGuardClient] = {}
        self._wireguard_connections: list[WireGuardClient] | None = None
        self._tailscale_config: dict[str, Any] = {}
        self._tailscale_connection: bool | None = None
        self._sms_messages: dict[str, SmsMessage] = {}

        self._late_init_complete = False
        self._connect_error = False
        self._token_error = False

    async def async_initialize_hub(self) -> None:
        if not self._late_init_complete:
            await self._async_load_router_info()

        entity_registry = er.async_get(self.hass)
        track_entries: list[RegistryEntry] = er.async_entries_for_config_entry(
            entity_registry, self._entry.entry_id
        )
        for entry in track_entries:
            if entry.domain == TRACKER_DOMAIN:
                self._devices[entry.unique_id] = ClientDeviceInfo(
                    entry.unique_id,
                    entry.original_name,
                )

        await self.refresh_session_token()
        await self.fetch_all_data()
        async_track_time_interval(self.hass, self._async_poll_update, SCAN_INTERVAL)

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
            router_info = await self._invoke_api(self._api.get_router_info)
        except (ClientError, TimeoutError, OSError) as exc:
            _LOGGER.exception("Error connecting to GL-INet router %s", self._host)
            raise ConfigEntryNotReady from exc
        except AuthenticationError as exc:
            raise ConfigEntryAuthFailed from exc

        if not router_info:
            raise ConfigEntryNotReady("Unable to retrieve router info during setup")

        self._model = str(router_info.get(CONF_MODEL, "UNKNOWN"))
        self._sw_version = str(router_info.get("firmware_version", "UNKNOWN"))
        self._factory_mac = str(router_info.get(CONF_MAC, "UNKNOWN"))
        self._late_init_complete = True

    async def refresh_session_token(self) -> None:
        api = self.router_api
        try:
            await api.authenticate(
                self._settings.get(CONF_USERNAME, DEFAULT_USERNAME),
                self._settings[CONF_PASSWORD],
            )
            _LOGGER.info("GL-INet router %s token was renewed", self._host)
        except (AuthenticationError, TokenError) as exc:
            _LOGGER.exception(
                "GL-INet router %s failed to renew the token",
                self._host,
            )
            raise ConfigEntryAuthFailed from exc

    async def fetch_all_data(self, _: datetime | None = None) -> None:
        await asyncio.gather(
            self.fetch_system_status(),
            self.fetch_internet_status(),
            self.fetch_connected_devices(),
            self.fetch_wifi_interfaces(),
            self.fetch_wireguard_clients(),
            self.fetch_tailscale_state(),
            self.fetch_cellular_status(),
        )
        await self.fetch_sms_messages()

    async def _async_poll_update(self, _: datetime | None = None) -> None:
        await self.fetch_all_data()

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
        except TokenError:
            if not self._connect_error:
                _LOGGER.warning(
                    "GL-INet router %s rejected the token; a reauthentication will be attempted",
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
        except (APIClientError, OSError, TimeoutError, ValueError):
            _LOGGER.debug("Optional GL-INet router API is unavailable", exc_info=True)
            return None

    async def fetch_system_status(self) -> None:
        response = await self._invoke_api(self.router_api.get_router_status)
        if response:
            status = dict(response)
            self._system_status = status | dict(status.get("system", {}))

    async def fetch_internet_status(self) -> None:
        response = await self._invoke_api(self.router_api.get_internet_status)
        if response:
            self._internet_status = dict(response)

    async def fetch_connected_devices(self) -> None:
        new_device = False
        connected_devices = await self._invoke_api(self.router_api.get_online_clients)
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
                continue

            new_device = True
            device = ClientDeviceInfo(device_mac)
            device.apply_update(dev_info)
            self._devices[device_mac] = device

        async_dispatcher_send(self.hass, self.event_device_updated)
        if new_device:
            async_dispatcher_send(self.hass, self.event_device_added)

    async def fetch_wifi_interfaces(self) -> None:
        response = await self._invoke_api(self.router_api.get_wifi_interfaces)
        if not response:
            return
        for name, iface in response.items():
            self._wifi_ifaces[name] = WifiInterface(
                name=name,
                enabled=bool(iface.get("enabled", False)),
                ssid=str(iface.get("ssid", "")),
                guest=bool(iface.get("guest", False)),
                hidden=bool(iface.get("hidden", False)),
                encryption=str(iface.get("encryption", "UNKNOWN")),
            )

    async def fetch_wireguard_clients(self) -> None:
        response = await self._invoke_api(self.router_api.get_wireguard_clients)
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

        state_response = await self._invoke_api(self.router_api.get_wireguard_state)
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

    async def fetch_tailscale_state(self) -> None:
        details = await self._invoke_optional_api(self.router_api.get_tailscale_details)
        if not details:
            self._tailscale_config = {}
            self._tailscale_connection = None
            return

        self._tailscale_config = details["config"]
        self._tailscale_connection = details["connection"] == TailscaleConnection.CONNECTED

    async def fetch_cellular_status(self) -> None:
        if self._cached_modem_info is None:
            info_response = await self._invoke_optional_api(self.router_api.get_modem_info)
            self._cached_modem_info = dict(info_response or {})
        else:
            info_response = self._cached_modem_info

        status_response = await self._invoke_optional_api(self.router_api.get_cellular_status)

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

    async def fetch_sms_messages(self) -> None:
        response = await self._invoke_optional_api(self.router_api.get_sms_messages)
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
                status=_first_int(item, ("status",)),
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
        response = await self._invoke_optional_api(
            lambda: self.router_api.send_sms(bus, recipient, text)
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

        await self._invoke_optional_api(lambda: self.router_api.remove_sms(bus, scope, message_id))
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
            name=self.name,
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
    def name(self) -> str:
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
    def active_vpn_connections(self) -> list[WireGuardClient] | None:
        return self._wireguard_connections

    @property
    def connected_vpn_clients(self) -> list[WireGuardClient] | None:
        return self._wireguard_connections

    @property
    def router_status(self) -> dict[str, Any]:
        return self._system_status

    @property
    def internet_status(self) -> dict[str, Any]:
        return self._internet_status

    @property
    def cellular_status(self) -> dict[str, Any]:
        return self._cellular_status

    @property
    def online_client_count(self) -> int:
        return sum(1 for device in self._devices.values() if device.is_connected)

    @property
    def total_client_rx_rate(self) -> int | None:
        rates = [device.rx_rate for device in self._devices.values() if device.rx_rate is not None]
        return sum(rates) if rates else None

    @property
    def total_client_tx_rate(self) -> int | None:
        rates = [device.tx_rate for device in self._devices.values() if device.tx_rate is not None]
        return sum(rates) if rates else None

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
    def sms_messages(self) -> dict[str, SmsMessage]:
        return self._sms_messages

    @property
    def default_modem_bus(self) -> str | None:
        return self._default_modem_bus

    @property
    def event_device_added(self) -> str:
        return f"{DOMAIN}-device-new-{self._factory_mac}"

    @property
    def event_device_updated(self) -> str:
        return f"{DOMAIN}-device-update-{self._factory_mac}"


def _first_bool(data: dict[str, Any], keys: tuple[str, ...]) -> bool | None:
    for key in keys:
        value = data.get(key)
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            return value != 0
        if isinstance(value, str):
            lowered = value.lower()
            if lowered in {"1", "true", "on", "enabled", "enable"}:
                return True
            if lowered in {"0", "false", "off", "disabled", "disable"}:
                return False
    return None


def _first_int(data: dict[str, Any], keys: tuple[str, ...]) -> int | None:
    for key in keys:
        value = data.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
    return None


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
