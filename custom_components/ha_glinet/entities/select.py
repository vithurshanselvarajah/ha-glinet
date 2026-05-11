from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.select import SelectEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..const import FEATURE_OVPN_CLIENT, FEATURE_REPEATER
from ..hub import GLinetHub
from ..models import OpenVpnClient

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)

NONE_SELECTED = "-- Select Network --"
HEADER_KNOWN = "-- Known Networks --"
HEADER_AVAILABLE = "-- Available Networks --"


BAND_AUTO = "Auto"
BAND_5GHZ = "5GHz"
BAND_24GHZ = "2.4GHz"

BAND_OPTIONS = [BAND_AUTO, BAND_5GHZ, BAND_24GHZ]
BAND_TO_API = {BAND_AUTO: None, BAND_5GHZ: "5g", BAND_24GHZ: "2g"}
API_TO_BAND = {None: BAND_AUTO, "5g": BAND_5GHZ, "2g": BAND_24GHZ}


async def async_setup_entry(
    _: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    hub: GLinetHub = entry.runtime_data
    entities: list[SelectEntity] = []
    if hub.feature_enabled(FEATURE_REPEATER):
        entities.extend([WifiNetworkSelect(hub), RepeaterBandSelect(hub)])

    if hub.feature_enabled(FEATURE_OVPN_CLIENT):
        for client in hub.ovpn_clients.values():
            if client.locations and len(client.locations) > 1:
                entities.append(OpenVpnClientLocationSelect(hub, client))

    async_add_entities(entities, True)


class WifiNetworkSelect(CoordinatorEntity[GLinetHub], SelectEntity):

    _attr_has_entity_name = True
    _attr_name = "WiFi network"
    _attr_icon = "mdi:wifi"
    _attr_current_option: str | None = None

    def __init__(self, hub: GLinetHub) -> None:
        super().__init__(hub)
        self._hub = hub
        self._attr_device_info = hub.device_info
        self._selected_ssid: str | None = None


    @property
    def unique_id(self) -> str:
        return f"glinet_select/{self._hub.device_mac}/wifi_network"

    @property
    def options(self) -> list[str]:
        options_list: list[str] = [NONE_SELECTED]
        seen: set[str] = set()

        saved = self._hub.saved_networks
        if saved:
            options_list.append(HEADER_KNOWN)
            for network in saved:
                ssid = network.get("ssid")
                if ssid and ssid not in seen:
                    seen.add(ssid)
                    options_list.append(ssid)

        scanned = self._hub.scanned_networks
        available_ssids: list[str] = []
        for network in sorted(scanned, key=lambda n: n.signal, reverse=True):
            if network.ssid and network.ssid not in seen:
                seen.add(network.ssid)
                available_ssids.append(network.ssid)

        if available_ssids:
            options_list.append(HEADER_AVAILABLE)
            options_list.extend(available_ssids)

        return options_list

    @property
    def current_option(self) -> str | None:
        status = self._hub.repeater_status
        if status and status.ssid:
            return status.ssid
        return self._selected_ssid or NONE_SELECTED

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        scanned = self._hub.scanned_networks
        saved = self._hub.saved_networks

        attrs: dict[str, Any] = {
            "known_count": len(saved),
            "scanned_count": len(set(n.ssid for n in scanned if n.ssid)),
            "last_scan": self._hub.last_wifi_scan,
        }

        selected = self.current_option
        if selected and selected not in (NONE_SELECTED, HEADER_KNOWN, HEADER_AVAILABLE):
            for network in scanned:
                if network.ssid == selected:
                    attrs["selected_signal"] = network.signal
                    attrs["selected_band"] = network.band
                    attrs["selected_channel"] = network.channel
                    attrs["selected_encryption"] = network.encryption_type
                    attrs["selected_saved"] = network.saved
                    break

        return attrs

    def _is_header(self, option: str) -> bool:
        return option in (NONE_SELECTED, HEADER_KNOWN, HEADER_AVAILABLE)

    def _is_saved_network(self, ssid: str) -> bool:
        return any(n.get("ssid") == ssid for n in self._hub.saved_networks)

    def _get_scanned_network(self, ssid: str) -> Any | None:
        for network in self._hub.scanned_networks:
            if network.ssid == ssid:
                return network
        return None

    async def async_select_option(self, option: str) -> None:
        if self._is_header(option):
            self._selected_ssid = None
            return

        self._selected_ssid = option

        if self._is_saved_network(option):
            _LOGGER.info("Connecting to saved network: %s", option)
            await self._hub.connect_to_wifi(ssid=option, remember=True)
            return

        scanned_network = self._get_scanned_network(option)
        if scanned_network and not scanned_network.encryption_enabled:
            _LOGGER.info("Connecting to open network: %s", option)
            await self._hub.connect_to_wifi(ssid=option, remember=False)
        else:
            _LOGGER.info(
                "Network '%s' requires password - use connect_wifi service to connect",
                option,
            )


class RepeaterBandSelect(CoordinatorEntity[GLinetHub], SelectEntity):

    _attr_has_entity_name = True
    _attr_name = "Repeater band"
    _attr_icon = "mdi:wifi-settings"
    _attr_options = BAND_OPTIONS

    def __init__(self, hub: GLinetHub) -> None:
        super().__init__(hub)
        self._hub = hub
        self._attr_device_info = hub.device_info

    @property
    def unique_id(self) -> str:
        return f"glinet_select/{self._hub.device_mac}/repeater_band"

    @property
    def current_option(self) -> str | None:
        band = self._hub.repeater_band
        return API_TO_BAND.get(band, BAND_AUTO)

    async def async_select_option(self, option: str) -> None:
        api_value = BAND_TO_API.get(option)
        await self._hub.set_repeater_band(api_value)
        self.async_write_ha_state()


class OpenVpnClientLocationSelect(CoordinatorEntity[GLinetHub], SelectEntity):
    _attr_has_entity_name = True
    _attr_icon = "mdi:map-marker-radius"

    def __init__(self, hub: GLinetHub, client: OpenVpnClient) -> None:
        super().__init__(hub)
        self._hub = hub
        self._client = client
        self._attr_device_info = hub.device_info

    @property
    def unique_id(self) -> str:
        key = f"{self._client.group_id}_{self._client.client_id}"
        return f"glinet_select/{self._hub.device_mac}/{key}/ovpn_location"

    @property
    def name(self) -> str:
        name = f"OpenVPN {self._client.name} location"
        if self._client.group_name:
             name = f"OpenVPN {self._client.group_name} {self._client.name} location"
        return name

    @property
    def options(self) -> list[str]:

        key = f"{self._client.group_id}_{self._client.client_id}"
        client = self._hub.ovpn_clients.get(key, self._client)
        return client.locations

    @property
    def current_option(self) -> str | None:
        key = f"{self._client.group_id}_{self._client.client_id}"
        client = self._hub.ovpn_clients.get(key, self._client)

        status = self._hub.ovpn_client_status

        if (
            status.get("group_id") == client.group_id
            and status.get("client_id") == client.client_id
        ):
            active_domain = status.get("domain")
            if active_domain:
                for i, remote in enumerate(client.remotes):
                    if active_domain in remote:
                        if i < len(client.locations):
                            return client.locations[i]



        current_config_remote = self._hub._ovpn_raw_clients.get(key, {}).get("remote")
        if isinstance(current_config_remote, list):

             return client.locations[0] if client.locations else None

        if current_config_remote:
             for i, remote in enumerate(client.remotes):
                 if current_config_remote == remote:
                     if i < len(client.locations):
                         return client.locations[i]

        return client.locations[0] if client.locations else None

    async def async_select_option(self, option: str) -> None:
        key = f"{self._client.group_id}_{self._client.client_id}"
        client = self._hub.ovpn_clients.get(key, self._client)

        if option in client.locations:
            index = client.locations.index(option)
            await self._hub.set_ovpn_client_location(client.group_id, client.client_id, index)
            self.async_write_ha_state()