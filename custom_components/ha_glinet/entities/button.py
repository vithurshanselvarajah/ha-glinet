from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.button import ButtonEntity
from homeassistant.const import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..const import FEATURE_REPEATER

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from ..hub import GLinetHub


async def async_setup_entry(
    _: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    hub: GLinetHub = entry.runtime_data
    entities = [RebootButton(hub), TestFanButton(hub)]
    if hub.feature_enabled(FEATURE_REPEATER):
        entities.extend([DisconnectRepeaterButton(hub), ScanWifiButton(hub)])
    async_add_entities(entities, True)


class RebootButton(CoordinatorEntity[GLinetHub], ButtonEntity):
    _attr_icon = "mdi:restart"
    _attr_has_entity_name = True

    def __init__(self, hub: GLinetHub) -> None:
        super().__init__(hub)
        self._hub = hub
        self._attr_device_info = hub.device_info

    @property
    def unique_id(self) -> str:
        return f"glinet_button/{self._hub.device_mac}/reboot"

    @property
    def entity_category(self) -> EntityCategory:
        return EntityCategory.CONFIG

    @property
    def name(self) -> str:
        return "Reboot"

    async def async_press(self) -> None:
        await self._hub.reboot()


class DisconnectRepeaterButton(CoordinatorEntity[GLinetHub], ButtonEntity):
    _attr_icon = "mdi:wifi-off"
    _attr_has_entity_name = True

    def __init__(self, hub: GLinetHub) -> None:
        super().__init__(hub)
        self._hub = hub
        self._attr_device_info = hub.device_info

    @property
    def unique_id(self) -> str:
        return f"glinet_button/{self._hub.device_mac}/disconnect_repeater"

    @property
    def entity_category(self) -> EntityCategory:
        return EntityCategory.CONFIG

    @property
    def name(self) -> str:
        return "Disconnect repeater"

    async def async_press(self) -> None:
        await self._hub.disconnect_wifi()


class ScanWifiButton(CoordinatorEntity[GLinetHub], ButtonEntity):
    _attr_icon = "mdi:wifi-sync"
    _attr_has_entity_name = True

    def __init__(self, hub: GLinetHub) -> None:
        super().__init__(hub)
        self._hub = hub
        self._attr_device_info = hub.device_info

    @property
    def unique_id(self) -> str:
        return f"glinet_button/{self._hub.device_mac}/scan_wifi"

    @property
    def entity_category(self) -> EntityCategory:
        return EntityCategory.CONFIG

    @property
    def name(self) -> str:
        return "Scan WiFi networks"

    async def async_press(self) -> None:
        await self._hub.scan_wifi_networks()

class TestFanButton(CoordinatorEntity[GLinetHub], ButtonEntity):
    _attr_has_entity_name = True
    _attr_name = "Fan test"
    _attr_translation_key = "test_fan"
    _attr_icon = "mdi:fan-alert"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, hub: GLinetHub) -> None:
        super().__init__(hub)
        self._hub = hub
        self._attr_device_info = hub.device_info

    @property
    def unique_id(self) -> str:
        return f"glinet_button/{self._hub.device_mac}/test_fan"

    async def async_press(self) -> None:
        await self._hub.test_fan(duration=10)
