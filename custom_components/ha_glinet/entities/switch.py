from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import EntityCategory

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from ..hub import GLinetHub
    from ..models import WifiInterface, WireGuardClient

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    _: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    hub: GLinetHub = entry.runtime_data
    entities: list[SwitchEntity] = [
        WireGuardSwitch(hub, client) for client in hub.vpn_clients.values()
    ]
    if hub.has_tailscale:
        entities.append(TailscaleSwitch(hub))
    entities.extend(WifiApSwitch(hub, name, iface) for name, iface in hub.wifi_interfaces.items())
    if entities:
        async_add_entities(entities, True)


class GLinetSwitchBase(SwitchEntity):
    _attr_has_entity_name = True

    def __init__(self, hub: GLinetHub) -> None:
        self._hub = hub
        self._attr_device_info = hub.device_info
        self._attr_is_on: bool | None = None

    @property
    def is_on(self) -> bool | None:
        return self._attr_is_on

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
    def icon(self) -> str:
        return "mdi:wifi" if self.is_on else "mdi:wifi-off"

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
            await self._hub.router_api.set_wifi_interface_enabled(self._iface_name, True)
        except OSError:
            _LOGGER.exception("Unable to enable WiFi interface %s", self._iface_name)
            return
        self._attr_is_on = True
        self.async_write_ha_state()
        await self._hub.fetch_wifi_interfaces()
        await self.async_update()

    async def async_turn_off(self, **_: Any) -> None:
        try:
            await self._hub.router_api.set_wifi_interface_enabled(self._iface_name, False)
        except OSError:
            _LOGGER.exception("Unable to disable WiFi interface %s", self._iface_name)
            return
        self._attr_is_on = False
        self.async_write_ha_state()
        await self._hub.fetch_wifi_interfaces()
        await self.async_update()

    async def async_update(self) -> None:
        self._iface = self._hub.wifi_interfaces.get(self._iface_name, self._iface)
        self._attr_is_on = self._iface.enabled


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

    async def async_turn_on(self, **_: Any) -> None:
        try:
            await self._hub.router_api.connect_tailscale()
        except OSError:
            _LOGGER.exception("Unable to enable tailscale connection")
            return
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **_: Any) -> None:
        try:
            await self._hub.router_api.disconnect_tailscale()
        except OSError:
            _LOGGER.exception("Unable to stop tailscale connection")
            return
        self._attr_is_on = False
        self.async_write_ha_state()

    async def async_update(self) -> None:
        await self._hub.fetch_tailscale_state()
        self._attr_is_on = self._hub.tailscale_connected

class WireGuardSwitch(GLinetSwitchBase):
    _attr_icon = "mdi:vpn"

    def __init__(self, hub: GLinetHub, client: WireGuardClient) -> None:
        super().__init__(hub)
        self._client = client
        self._attr_is_on = False

    @property
    def unique_id(self) -> str:
        return f"glinet_switch/{self._hub.device_mac}/{self._client.name}/wireguard_client"

    @property
    def name(self) -> str:
        return f"WG Client {self._client.name}"

    async def async_turn_on(self, **_: Any) -> None:
        try:
            if (
                self._client.tunnel_id is None
                and self._hub.connected_vpn_clients is not None
                and self._client not in self._hub.connected_vpn_clients
            ):
                for client in self._hub.connected_vpn_clients:
                    await self._hub.router_api.stop_wireguard_client(client.peer_id)

            await self._hub.router_api.start_wireguard_client(
                self._client.group_id,
                self._client.tunnel_id or self._client.peer_id,
            )
        except OSError:
            _LOGGER.exception("Unable to enable WireGuard client")
            return
        self._attr_is_on = True
        self.async_write_ha_state()
        await self._hub.fetch_wireguard_clients()
        await self.async_update()

    async def async_turn_off(self, **_: Any) -> None:
        try:
            await self._hub.router_api.stop_wireguard_client(
                self._client.tunnel_id or self._client.peer_id
            )
        except OSError:
            _LOGGER.exception("Unable to stop WireGuard client")
            return
        self._attr_is_on = False
        self.async_write_ha_state()
        await self._hub.fetch_wireguard_clients()
        await self.async_update()

    async def async_update(self) -> None:
        current = self._hub.vpn_clients.get(self._client.peer_id)
        if current is not None:
            self._client = current
        self._attr_is_on = self._client in (self._hub.active_vpn_connections or [])
