from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import EntityCategory
from homeassistant.core import callback
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC, format_mac
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..const import (
    DOMAIN,
    FEATURE_ADGUARD,
    FEATURE_FIREWALL,
    FEATURE_OVPN_CLIENT,
    FEATURE_OVPN_SERVER,
    FEATURE_PARENTAL_CONTROL,
    FEATURE_REPEATER,
    FEATURE_TAILSCALE,
    FEATURE_WG_CLIENT,
    FEATURE_WG_SERVER,
    FEATURE_ZEROTIER,
)
from ..hub import GLinetHub
from ..models import (
    ClientDeviceInfo,
    OpenVpnClient,
    ParentalGroup,
    VpnTunnel,
    VpnTunnelType,
    WifiInterface,
    WireGuardClient,
)

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
    # 4.9+ exposes a unified VPN dashboard. When tunnels are present we
    # surface those as switches instead of the per-profile entries from 4.8.
    dashboard_tunnels: list[VpnTunnel] = []
    if hub.feature_enabled(FEATURE_WG_CLIENT) or hub.feature_enabled(FEATURE_OVPN_CLIENT):
        for tunnel in hub.vpn_tunnels.values():
            if tunnel.tunnel_type == VpnTunnelType.WIREGUARD and hub.feature_enabled(
                FEATURE_WG_CLIENT
            ):
                dashboard_tunnels.append(tunnel)
            elif tunnel.tunnel_type == VpnTunnelType.OPENVPN and hub.feature_enabled(
                FEATURE_OVPN_CLIENT
            ):
                dashboard_tunnels.append(tunnel)
            elif tunnel.tunnel_type == VpnTunnelType.UNKNOWN:
                # Show unknown-typed tunnels if either client feature is on;
                # the user can still toggle them via the dashboard.
                if hub.feature_enabled(FEATURE_WG_CLIENT) or hub.feature_enabled(
                    FEATURE_OVPN_CLIENT
                ):
                    dashboard_tunnels.append(tunnel)

    if dashboard_tunnels:
        entities.extend(VpnTunnelSwitch(hub, tunnel) for tunnel in dashboard_tunnels)
    else:
        if hub.feature_enabled(FEATURE_WG_CLIENT):
            entities.extend(WireGuardSwitch(hub, client) for client in hub.vpn_clients.values())
        if hub.feature_enabled(FEATURE_OVPN_CLIENT):
            entities.extend(
                OpenVpnClientSwitch(hub, client) for client in hub.ovpn_clients.values()
            )
    if hub.feature_enabled(FEATURE_WG_SERVER):
        entities.append(WireGuardServerSwitch(hub))
    if hub.feature_enabled(FEATURE_OVPN_SERVER):
        entities.append(OpenVpnServerSwitch(hub))
    if hub.has_tailscale and hub.feature_enabled(FEATURE_TAILSCALE):
        entities.append(TailscaleSwitch(hub))
    if hub.has_zerotier and hub.feature_enabled(FEATURE_ZEROTIER):
        entities.append(ZeroTierSwitch(hub))
    entities.extend(WifiApSwitch(hub, name, iface) for name, iface in hub.wifi_interfaces.items())
    if hub.feature_enabled(FEATURE_REPEATER):
        entities.extend(
            [
                RepeaterAutoSwitchSwitch(hub),
                RepeaterBareModeSwitch(hub),
                RepeaterSmartReconnectSwitch(hub),
            ]
        )
    if hub.feature_enabled(FEATURE_ADGUARD):
        entities.append(AdGuardEnabledSwitch(hub))
        entities.append(AdGuardDnsEnabledSwitch(hub))
    if hub.feature_enabled(FEATURE_FIREWALL):
        entities.append(GLinetDMZSwitch(hub))
        entities.append(GLinetWANAccessSwitch(hub, "ping", "WAN Ping", "mdi:access-point-network"))
        entities.append(GLinetWANAccessSwitch(hub, "https", "WAN HTTPS Access", "mdi:web"))
        entities.append(GLinetWANAccessSwitch(hub, "ssh", "WAN SSH Access", "mdi:console-network"))
    if hub.feature_enabled(FEATURE_PARENTAL_CONTROL):
        entities.append(GLinetParentalControlGlobalSwitch(hub))
        entities.extend(
            GLinetParentalControlGroupSwitch(hub, group) for group in hub.parental_groups.values()
        )
    entities.append(LedSwitch(hub))
    async_add_entities(entities, True)

    # ------------------------------------------------------------------
    # Live reconciliation for VPN dashboard tunnels (4.9+)
    # ------------------------------------------------------------------
    # When a profile is removed from the router, the corresponding tunnel
    # disappears from `vpn-client.get_tunnel`. The hub dispatches the
    # ``event_vpn_tunnels_updated`` event after every fetch with the new set
    # of tunnel ids, so we use it to add new switches and remove stale ones
    # automatically. This keeps Home Assistant in lockstep with whatever is
    # currently configured on the router.
    # VpnTunnelSwitch is defined further down in this module; the type
    # annotation has to be a string here because of the forward reference.
    vpn_tunnel_switches: "dict[int, VpnTunnelSwitch]" = {  # noqa: UP037
        entity._tunnel_id: entity for entity in entities if isinstance(entity, VpnTunnelSwitch)
    }

    def _candidate_tunnels_for_features() -> list[VpnTunnel]:
        result: list[VpnTunnel] = []
        for tunnel in hub.vpn_tunnels.values():
            if tunnel.tunnel_type == VpnTunnelType.WIREGUARD and hub.feature_enabled(
                FEATURE_WG_CLIENT
            ):
                result.append(tunnel)
            elif tunnel.tunnel_type == VpnTunnelType.OPENVPN and hub.feature_enabled(
                FEATURE_OVPN_CLIENT
            ):
                result.append(tunnel)
            elif tunnel.tunnel_type == VpnTunnelType.UNKNOWN and (
                hub.feature_enabled(FEATURE_WG_CLIENT) or hub.feature_enabled(FEATURE_OVPN_CLIENT)
            ):
                result.append(tunnel)
        return result

    @callback
    def _reconcile_vpn_tunnels(current_ids: set[int] | None = None) -> None:
        hass = hub.hass
        hass.async_create_task(_async_reconcile_vpn_tunnels(current_ids))

    async def _async_reconcile_vpn_tunnels(
        current_ids: set[int] | None = None,
    ) -> None:
        if current_ids is None:
            current_ids = {t.tunnel_id for t in _candidate_tunnels_for_features()}

        existing_ids = set(vpn_tunnel_switches.keys())

        # Add new tunnels that have appeared since the last fetch.
        new_tunnels = [
            tunnel
            for tunnel in _candidate_tunnels_for_features()
            if tunnel.tunnel_id not in existing_ids and tunnel.tunnel_id in current_ids
        ]
        if new_tunnels:
            new_entities = [VpnTunnelSwitch(hub, tunnel) for tunnel in new_tunnels]
            for entity in new_entities:
                vpn_tunnel_switches[entity._tunnel_id] = entity
            async_add_entities(new_entities, True)

        # Remove tunnels that disappeared from the router.
        stale_ids = existing_ids - current_ids
        if stale_ids:
            registry = async_get_entity_registry(hub.hass)
            for stale_id in list(stale_ids):
                entity = vpn_tunnel_switches.pop(stale_id, None)
                if entity is None:
                    continue
                # ``Entity.async_remove`` is a coroutine; it must be
                # awaited for the entity to be detached from the platform.
                # ``force_remove=True`` clears the entity state immediately
                # rather than marking it as unavailable.
                await entity.async_remove(force_remove=True)
                # ``Entity.async_remove`` only removes the state — the
                # entry in the Entity Registry survives unless we also
                # drop it. Without this, the user still sees the entity
                # (with state "unavailable") and cannot delete it from
                # the UI. Removing the registry entry makes the entity
                # disappear from Home Assistant completely.
                if entity.entity_id:
                    registry.async_remove(entity.entity_id)

    entry.async_on_unload(
        async_dispatcher_connect(
            hub.hass,
            hub.event_vpn_tunnels_updated,
            _reconcile_vpn_tunnels,
        )
    )

    if hub.feature_enabled(FEATURE_PARENTAL_CONTROL):
        tracked: set[str] = set()

        @callback
        def register_new_devices() -> None:
            new_entities = [
                GLinetClientInternetAccessSwitch(hub, device)
                for mac, device in hub.tracked_devices.items()
                if mac not in tracked
            ]
            for entity in new_entities:
                tracked.add(entity._device.mac)
            if new_entities:
                async_add_entities(new_entities, True)

        register_new_devices()
        entry.async_on_unload(
            async_dispatcher_connect(
                hub.hass,
                hub.event_device_added,
                register_new_devices,
            )
        )


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
                    await self._hub.stop_vpn_client(client.group_id, client.peer_id)

            await self._hub.start_vpn_client(
                self._client.group_id,
                self._client.peer_id,
            )
        except OSError:
            _LOGGER.exception("Unable to enable WireGuard client")
            return
        await self._hub.async_request_refresh()

    async def async_turn_off(self, **_: Any) -> None:
        try:
            await self._hub.stop_vpn_client(
                self._client.group_id,
                self._client.peer_id,
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


class RepeaterBareModeSwitch(GLinetSwitchBase):
    _attr_icon = "mdi:wifi-off"
    _attr_translation_key = "repeater_bare_mode"

    @property
    def unique_id(self) -> str:
        return f"glinet_switch/{self._hub.device_mac}/repeater_bare_mode"

    @property
    def is_on(self) -> bool | None:
        return self._hub.repeater_bare_mode

    async def async_turn_on(self, **_: Any) -> None:
        try:
            await self._hub.set_repeater_bare_mode(True)
        except OSError:
            _LOGGER.exception("Unable to enable repeater bare mode")
            return
        await self._hub.async_request_refresh()

    async def async_turn_off(self, **_: Any) -> None:
        try:
            await self._hub.set_repeater_bare_mode(False)
        except OSError:
            _LOGGER.exception("Unable to disable repeater bare mode")
            return
        await self._hub.async_request_refresh()


class RepeaterSmartReconnectSwitch(GLinetSwitchBase):
    _attr_icon = "mdi:wifi-refresh"
    _attr_translation_key = "repeater_smart_reconnect"

    @property
    def unique_id(self) -> str:
        return f"glinet_switch/{self._hub.device_mac}/repeater_smart_reconnect"

    @property
    def is_on(self) -> bool | None:
        return self._hub.repeater_smart_reconnect

    async def async_turn_on(self, **_: Any) -> None:
        try:
            await self._hub.set_repeater_smart_reconnect(True)
        except OSError:
            _LOGGER.exception("Unable to enable repeater smart reconnect")
            return
        await self._hub.async_request_refresh()

    async def async_turn_off(self, **_: Any) -> None:
        try:
            await self._hub.set_repeater_smart_reconnect(False)
        except OSError:
            _LOGGER.exception("Unable to disable repeater smart reconnect")
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
            await self._hub.stop_ovpn_client(
                self._client.group_id, self._client.client_id, self._client.tunnel_id
            )
        except OSError:
            _LOGGER.exception("Unable to stop OpenVPN client")
            return
        await asyncio.sleep(10)
        await self._hub.async_request_refresh()


class VpnTunnelSwitch(GLinetSwitchBase):
    _attr_icon = "mdi:vpn"

    def __init__(self, hub: GLinetHub, tunnel: VpnTunnel) -> None:
        super().__init__(hub)
        self._tunnel_id = tunnel.tunnel_id
        self._tunnel_type = tunnel.tunnel_type
        self._cached_tunnel = tunnel

    def _current_tunnel(self) -> VpnTunnel | None:
        tunnel = self._hub.vpn_tunnels.get(self._tunnel_id)
        if tunnel is not None:
            self._cached_tunnel = tunnel
        return tunnel

    @property
    def _tunnel(self) -> VpnTunnel:
        return self._current_tunnel() or self._cached_tunnel

    @property
    def unique_id(self) -> str:
        if self._tunnel_type in {VpnTunnelType.WIREGUARD, VpnTunnelType.OPENVPN}:
            type_token = "wg" if self._tunnel_type == VpnTunnelType.WIREGUARD else "ovpn"
            return f"glinet_switch/{self._hub.device_mac}/vpn_tunnel/{type_token}/{self._tunnel_id}"
        # Unknown type - keep the tunnel prefix so both WG and OVPN feature
        # cleanup can find it if either feature is later disabled.
        return f"glinet_switch/{self._hub.device_mac}/vpn_tunnel/unknown/{self._tunnel_id}"

    @property
    def name(self) -> str:
        tunnel = self._tunnel
        tunnel_name = tunnel.name or f"Tunnel {self._tunnel_id}"
        if self._tunnel_type == VpnTunnelType.WIREGUARD:
            return f"WG Tunnel {tunnel_name}"
        if self._tunnel_type == VpnTunnelType.OPENVPN:
            return f"OpenVPN Tunnel {tunnel_name}"
        return f"VPN Tunnel {tunnel_name}"

    @property
    def is_on(self) -> bool | None:
        return self._tunnel.enabled

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        tunnel = self._tunnel
        return {
            "tunnel_id": tunnel.tunnel_id,
            "tunnel_type": tunnel.tunnel_type.value,
            "connected": tunnel.connected,
            "killswitch": tunnel.killswitch,
            "is_default": tunnel.is_default,
            "via": tunnel.via,
        }

    async def async_turn_on(self, **_: Any) -> None:
        try:
            await self._hub.set_vpn_tunnel(self._tunnel_id, True)
        except OSError:
            _LOGGER.exception("Unable to enable VPN tunnel %s", self._tunnel_id)
            return
        await self._hub.async_request_refresh()

    async def async_turn_off(self, **_: Any) -> None:
        try:
            await self._hub.set_vpn_tunnel(self._tunnel_id, False)
        except OSError:
            _LOGGER.exception("Unable to disable VPN tunnel %s", self._tunnel_id)
            return
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


class ZeroTierSwitch(GLinetSwitchBase):
    @property
    def unique_id(self) -> str:
        return f"glinet_switch/{self._hub.device_mac}/zerotier"

    @property
    def name(self) -> str:
        return "ZeroTier"

    @property
    def icon(self) -> str:
        return "mdi:lan-connect"

    @property
    def is_on(self) -> bool | None:
        if self._hub.zerotier_status is None:
            return None
        return self._hub.zerotier_status.enabled

    async def async_turn_on(self, **_: Any) -> None:
        await self._hub.start_zerotier()
        await self._hub.async_request_refresh()

    async def async_turn_off(self, **_: Any) -> None:
        await self._hub.stop_zerotier()
        await self._hub.async_request_refresh()

    @property
    def available(self) -> bool:
        if not super().available:
            return False
        status = self._hub.zerotier_status
        return bool(status and status.network_id)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        if status := self._hub.zerotier_status:
            attrs = {
                "network_id": status.network_id,
                "connected": status.connected,
                "zerotier_ip": status.zerotier_ip,
                "lan_ip": status.lan_ip,
                "wan_ip": status.wan_ip,
            }
            if not status.network_id:
                attrs["note"] = "Add ZeroTier Network ID in router settings"
            return attrs
        return {}


class LedSwitch(GLinetSwitchBase):
    _attr_icon = "mdi:led-on"

    @property
    def unique_id(self) -> str:
        return f"glinet_switch/{self._hub.device_mac}/led"

    @property
    def name(self) -> str:
        return "System LED"

    @property
    def is_on(self) -> bool | None:
        return self._hub.led_enabled

    async def async_turn_on(self, **_: Any) -> None:
        await self._hub.set_led_enabled(True)
        await self._hub.async_request_refresh()

    async def async_turn_off(self, **_: Any) -> None:
        await self._hub.set_led_enabled(False)
        await self._hub.async_request_refresh()


class AdGuardEnabledSwitch(GLinetSwitchBase):
    @property
    def unique_id(self) -> str:
        return f"glinet_switch/{self._hub.device_mac}/adguard_enabled"

    @property
    def translation_key(self) -> str:
        return "adguard_enabled"

    @property
    def icon(self) -> str:
        return "mdi:shield-check"

    @property
    def is_on(self) -> bool | None:
        status = self._hub.adguard_status
        return status.enabled if status else None

    async def async_turn_on(self, **_: Any) -> None:
        await self._hub.set_adguard_enabled(True)
        await self._hub.async_request_refresh()

    async def async_turn_off(self, **_: Any) -> None:
        await self._hub.set_adguard_enabled(False)
        await self._hub.async_request_refresh()


class AdGuardDnsEnabledSwitch(GLinetSwitchBase):
    @property
    def unique_id(self) -> str:
        return f"glinet_switch/{self._hub.device_mac}/adguard_dns_enabled"

    @property
    def translation_key(self) -> str:
        return "adguard_dns_enabled"

    @property
    def icon(self) -> str:
        return "mdi:dns"

    @property
    def is_on(self) -> bool | None:
        status = self._hub.adguard_status
        return status.dns_enabled if status else None

    async def async_turn_on(self, **_: Any) -> None:
        await self._hub.set_adguard_dns_enabled(True)
        await self._hub.async_request_refresh()

    async def async_turn_off(self, **_: Any) -> None:
        await self._hub.set_adguard_dns_enabled(False)
        await self._hub.async_request_refresh()


class GLinetDMZSwitch(GLinetSwitchBase):
    _attr_icon = "mdi:shield-off"

    @property
    def unique_id(self) -> str:
        return f"glinet_switch/{self._hub.device_mac}/firewall_dmz"

    @property
    def name(self) -> str:
        return "Firewall DMZ"

    @property
    def is_on(self) -> bool | None:
        return self._hub._dmz_config.get("enabled", False)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {"destination_ip": self._hub._dmz_config.get("dest_ip")}

    async def async_turn_on(self, **_: Any) -> None:
        _LOGGER.warning(
            "DMZ cannot be enabled without a destination IP. Use the service to configure."
        )

    async def async_turn_off(self, **_: Any) -> None:
        await self._hub.set_dmz_config(False)
        await self._hub.async_request_refresh()


class GLinetWANAccessSwitch(GLinetSwitchBase):
    def __init__(self, hub: GLinetHub, access_type: str, name: str, icon: str) -> None:
        super().__init__(hub)
        self._access_type = access_type
        self._name = name
        self._attr_icon = icon

    @property
    def unique_id(self) -> str:
        return f"glinet_switch/{self._hub.device_mac}/wan_access_{self._access_type}"

    @property
    def name(self) -> str:
        return self._name

    @property
    def is_on(self) -> bool | None:
        return self._hub._wan_access.get(f"enable_{self._access_type}", False)

    async def async_turn_on(self, **_: Any) -> None:
        config = self._hub._wan_access.copy()
        config[f"enable_{self._access_type}"] = True
        await self._hub.set_wan_access(config)
        await self._hub.async_request_refresh()

    async def async_turn_off(self, **_: Any) -> None:
        config = self._hub._wan_access.copy()
        config[f"enable_{self._access_type}"] = False
        await self._hub.set_wan_access(config)
        await self._hub.async_request_refresh()


class GLinetParentalControlGlobalSwitch(GLinetSwitchBase):
    _attr_icon = "mdi:account-child"

    @property
    def unique_id(self) -> str:
        return f"glinet_switch/{self._hub.device_mac}/parental_control"

    @property
    def name(self) -> str:
        return "Parental control"

    @property
    def is_on(self) -> bool | None:
        return self._hub.parental_control_enabled

    async def async_turn_on(self, **_: Any) -> None:
        await self._hub.set_parental_control_enabled(True)
        await self._hub.async_request_refresh()

    async def async_turn_off(self, **_: Any) -> None:
        await self._hub.set_parental_control_enabled(False)
        await self._hub.async_request_refresh()


class GLinetParentalControlGroupSwitch(GLinetSwitchBase):
    _attr_icon = "mdi:account-group"

    def __init__(self, hub: GLinetHub, group: ParentalGroup) -> None:
        super().__init__(hub)
        self._group = group

    @property
    def unique_id(self) -> str:
        return f"glinet_switch/{self._hub.device_mac}/parental_control_group_{self._group.id}"

    @property
    def name(self) -> str:
        return f"Parental control {self._group.name}"

    @property
    def is_on(self) -> bool | None:
        self._group = self._hub.parental_groups.get(self._group.id, self._group)
        return self._group.enabled

    async def async_turn_on(self, **_: Any) -> None:
        await self._hub.set_group_enabled(self._group.id, True)
        await self._hub.async_request_refresh()

    async def async_turn_off(self, **_: Any) -> None:
        await self._hub.set_group_enabled(self._group.id, False)
        await self._hub.async_request_refresh()


class GLinetClientInternetAccessSwitch(GLinetSwitchBase):
    _attr_icon = "mdi:web-check"

    def __init__(self, hub: GLinetHub, device: ClientDeviceInfo) -> None:
        super().__init__(hub)
        self._device = device
        self._attr_device_info = DeviceInfo(
            connections={(CONNECTION_NETWORK_MAC, format_mac(device.mac))},
            name=device.name or device.mac,
            via_device=(DOMAIN, self._hub.router_id),
        )

    @property
    def unique_id(self) -> str:
        return f"glinet_switch/{self._device.mac}/internet_access"

    @property
    def name(self) -> str:
        return "Internet access"

    @property
    def is_on(self) -> bool | None:
        return self._hub.device_internet_access_enabled(self._device.mac)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {"access_control_mode": self._hub.access_control_mode}

    async def async_turn_on(self, **_: Any) -> None:
        await self._hub.set_single_device_block(self._device.mac, False)
        await self._hub.async_request_refresh()

    async def async_turn_off(self, **_: Any) -> None:
        await self._hub.set_single_device_block(self._device.mac, True)
        await self._hub.async_request_refresh()
