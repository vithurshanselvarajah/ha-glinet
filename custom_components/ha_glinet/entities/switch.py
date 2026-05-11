from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..const import (
    FEATURE_OVPN_CLIENT,
    FEATURE_OVPN_SERVER,
    FEATURE_REPEATER,
    FEATURE_TAILSCALE,
    FEATURE_WG_CLIENT,
    FEATURE_WG_SERVER,
)
from ..hub import GLinetHub
from ..models import OpenVpnClient, WifiInterface, WireGuardClient

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    _: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    hub: GLinetHub = entry.runtime_data
    entities: list[SwitchEntity] = []
    if hub.feature_enabled(FEATURE_WG_CLIENT):
        entities.extend(WireGuardSwitch(hub, client) for client in hub.vpn_clients.values())
    if hub.feature_enabled(FEATURE_WG_SERVER):
        entities.append(WireGuardServerSwitch(hub))
    if hub.feature_enabled(FEATURE_OVPN_CLIENT):
        entities.extend(OpenVpnClientSwitch(hub, client) for client in hub.ovpn_clients.values())
    if hub.feature_enabled(FEATURE_OVPN_SERVER):
        entities.append(OpenVpnServerSwitch(hub))
    if hub.has_tailscale and hub.feature_enabled(FEATURE_TAILSCALE):
        entities.append(TailscaleSwitch(hub))
    entities.extend(WifiApSwitch(hub, name, iface) for name, iface in hub.wifi_interfaces.items())
    if hub.feature_enabled(FEATURE_REPEATER):
        entities.append(RepeaterAutoSwitchSwitch(hub))
    async_add_entities(entities, True)


class GLinetSwitchBase(CoordinatorEntity[GLinetHub], SwitchEntity):
    _attr_has_entity_name = True

    def __init__(self, hub: GLinetHub) -> None:
        super().__init__(hub)
        self._hub = hub
        self._attr_device_info = hub.device_info

    @property
    def entity_category(self) -> EntityCategory:
        return EntityCategory.CONFIG


class WifiApSwitch(GLinetSwitchBase):
    def __init__(self, hub: GLinetHub, iface_name: str, iface: WifiInterface) -> None:
        super().__init__(hub)
        self._iface_name = iface_name
        self._iface = iface

    @property
    def unique_id(self) -> str:
        return f"glinet_switch/{self._hub.device_mac}/iface_{self._iface_name}"

    @property
    def name(self) -> str:
        return self._iface.ssid or self._iface.name

    @property
    def is_on(self) -> bool | None:
        self._iface = self._hub.wifi_interfaces.get(self._iface_name, self._iface)
        return self._iface.enabled

    @property
    def extra_state_attributes(self) -> dict[str, str | bool]:
        return {
            "interface": self._iface.name,
            "guest": self._iface.guest,
            "ssid": self._iface.ssid,
            "hidden": self._iface.hidden,
            "encryption": self._iface.encryption,
        }

    async def async_turn_on(self, **_: Any) -> None:
        try:
            await self._hub.set_wifi_interface_enabled(self._iface_name, True)
        except OSError:
            _LOGGER.exception("Unable to enable WiFi interface %s", self._iface_name)
            return
        await self._hub.async_request_refresh()

    async def async_turn_off(self, **_: Any) -> None:
        try:
            await self._hub.set_wifi_interface_enabled(self._iface_name, False)
        except OSError:
            _LOGGER.exception("Unable to disable WiFi interface %s", self._iface_name)
            return
        await self._hub.async_request_refresh()



class TailscaleSwitch(GLinetSwitchBase):
    _attr_icon = "mdi:vpn"

    @property
    def unique_id(self) -> str:
        return f"glinet_switch/{self._hub.device_mac}/tailscale"

    @property
    def name(self) -> str:
        return "Tailscale"

    @property
    def entity_registry_enabled_default(self) -> bool:
        return self._hub.has_tailscale

    @property
    def entity_registry_visible_default(self) -> bool:
        return self._hub.has_tailscale

    @property
    def is_on(self) -> bool | None:
        return self._hub.tailscale_connected

    async def async_turn_on(self, **_: Any) -> None:
        try:
            await self._hub.connect_tailscale()
        except OSError:
            _LOGGER.exception("Unable to enable tailscale connection")
            return
        await self._hub.async_request_refresh()

    async def async_turn_off(self, **_: Any) -> None:
        try:
            await self._hub.disconnect_tailscale()
        except OSError:
            _LOGGER.exception("Unable to stop tailscale connection")
            return
        await self._hub.async_request_refresh()

class WireGuardSwitch(GLinetSwitchBase):
    _attr_icon = "mdi:vpn"

    def __init__(self, hub: GLinetHub, client: WireGuardClient) -> None:
        super().__init__(hub)
        self._client = client
    @property
    def unique_id(self) -> str:
        return f"glinet_switch/{self._hub.device_mac}/{self._client.name}/wireguard_client"

    @property
    def name(self) -> str:
        return f"WG Client {self._client.name}"

    @property
    def is_on(self) -> bool | None:
        current = self._hub.vpn_clients.get(self._client.peer_id)
        if current is not None:
            self._client = current
        return self._client.connected

    async def async_turn_on(self, **_: Any) -> None:
        try:
            if (
                self._client.tunnel_id is None
                and self._hub.connected_vpn_clients is not None
                and self._client not in self._hub.connected_vpn_clients
            ):
                for client in self._hub.connected_vpn_clients:
                    await self._hub.stop_vpn_client(client.peer_id)

            await self._hub.start_vpn_client(
                self._client.group_id,
                self._client.tunnel_id or self._client.peer_id,
            )
        except OSError:
            _LOGGER.exception("Unable to enable WireGuard client")
            return
        await self._hub.async_request_refresh()

    async def async_turn_off(self, **_: Any) -> None:
        try:
            await self._hub.stop_vpn_client(
                self._client.tunnel_id or self._client.peer_id
            )
        except OSError:
            _LOGGER.exception("Unable to stop WireGuard client")
            return
        await self._hub.async_request_refresh()


class WireGuardServerSwitch(GLinetSwitchBase):
    _attr_icon = "mdi:vpn"

    @property
    def unique_id(self) -> str:
        return f"glinet_switch/{self._hub.device_mac}/wg_server"

    @property
    def name(self) -> str:
        return "WG Server"

    @property
    def is_on(self) -> bool | None:
        status = self._hub.wg_server_status
        return status.enabled if status else None

    async def async_turn_on(self, **_: Any) -> None:
        try:
            await self._hub.start_wg_server()
        except OSError:
            _LOGGER.exception("Unable to start WireGuard server")
            return
        await asyncio.sleep(10)
        await self._hub.async_request_refresh()

    async def async_turn_off(self, **_: Any) -> None:
        try:
            await self._hub.stop_wg_server()
        except OSError:
            _LOGGER.exception("Unable to stop WireGuard server")
            return
        await asyncio.sleep(10)
        await self._hub.async_request_refresh()



class RepeaterAutoSwitchSwitch(GLinetSwitchBase):
    _attr_icon = "mdi:wifi-sync"

    @property
    def unique_id(self) -> str:
        return f"glinet_switch/{self._hub.device_mac}/repeater_auto_switch"

    @property
    def name(self) -> str:
        return "Repeater auto-switch networks"

    @property
    def is_on(self) -> bool | None:
        return self._hub.repeater_auto_switch

    async def async_turn_on(self, **_: Any) -> None:
        try:
            await self._hub.set_repeater_auto_switch(True)
        except OSError:
            _LOGGER.exception("Unable to enable repeater auto-switch")
            return
        await self._hub.async_request_refresh()

    async def async_turn_off(self, **_: Any) -> None:
        try:
            await self._hub.set_repeater_auto_switch(False)
        except OSError:
            _LOGGER.exception("Unable to disable repeater auto-switch")
            return
        await self._hub.async_request_refresh()


class OpenVpnClientSwitch(GLinetSwitchBase):
    _attr_icon = "mdi:vpn"

    def __init__(self, hub: GLinetHub, client: OpenVpnClient) -> None:
        super().__init__(hub)
        self._client = client

    @property
    def unique_id(self) -> str:
        key = f"{self._client.group_id}_{self._client.client_id}"
        return f"glinet_switch/{self._hub.device_mac}/{key}/ovpn_client"

    @property
    def name(self) -> str:
        name = f"OpenVPN {self._client.name}"
        if self._client.group_name:
             name = f"OpenVPN {self._client.group_name} {self._client.name}"
        return name

    @property
    def is_on(self) -> bool | None:
        key = f"{self._client.group_id}_{self._client.client_id}"
        current = self._hub.ovpn_clients.get(key)
        if current is not None:
            self._client = current
        return self._client.connected

    async def async_turn_on(self, **_: Any) -> None:
        try:
            if (
                self._hub.connected_ovpn_clients
                and self._client not in self._hub.connected_ovpn_clients
            ):
                await self._hub.stop_ovpn_client()

            await self._hub.start_ovpn_client(
                self._client.group_id,
                self._client.client_id,
            )
        except OSError:
            _LOGGER.exception("Unable to enable OpenVPN client")
            return
        await asyncio.sleep(10)
        await self._hub.async_request_refresh()

    async def async_turn_off(self, **_: Any) -> None:
        try:
            await self._hub.stop_ovpn_client()
        except OSError:
            _LOGGER.exception("Unable to stop OpenVPN client")
            return
        await asyncio.sleep(10)
        await self._hub.async_request_refresh()


class OpenVpnServerSwitch(GLinetSwitchBase):
    _attr_icon = "mdi:vpn"

    @property
    def unique_id(self) -> str:
        return f"glinet_switch/{self._hub.device_mac}/ovpn_server"

    @property
    def name(self) -> str:
        return "OpenVPN Server"

    @property
    def is_on(self) -> bool | None:
        status = self._hub.ovpn_server_status
        return status.enabled if status else None

    async def async_turn_on(self, **_: Any) -> None:
        try:
            await self._hub.start_ovpn_server()
        except OSError:
            _LOGGER.exception("Unable to start OpenVPN server")
            return
        await asyncio.sleep(10)
        await self._hub.async_request_refresh()

    async def async_turn_off(self, **_: Any) -> None:
        try:
            await self._hub.stop_ovpn_server()
        except OSError:
            _LOGGER.exception("Unable to stop OpenVPN server")
            return
        await asyncio.sleep(10)
        await self._hub.async_request_refresh()
