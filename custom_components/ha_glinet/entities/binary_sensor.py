from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.const import EntityCategory

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
    entities = [InternetStatusBinarySensor(hub), FanRunningBinarySensor(hub)]
    if hub.feature_enabled(FEATURE_REPEATER):
        entities.append(RepeaterConnectedBinarySensor(hub))
    async_add_entities(entities, True)


class InternetStatusBinarySensor(BinarySensorEntity):

    _attr_has_entity_name = True
    _attr_name = "Internet"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, hub: GLinetHub) -> None:
        self._hub = hub
        self._attr_device_info = hub.device_info

    @property
    def unique_id(self) -> str:
        return f"glinet_binary_sensor/{self._hub.device_mac}/internet"

    @property
    def is_on(self) -> bool | None:
        return _internet_is_connected(self._hub.internet_status)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return self._hub.internet_status


class RepeaterConnectedBinarySensor(BinarySensorEntity):

    _attr_has_entity_name = True
    _attr_name = "Repeater connected"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_icon = "mdi:wifi-sync"

    def __init__(self, hub: GLinetHub) -> None:
        self._hub = hub
        self._attr_device_info = hub.device_info

    @property
    def unique_id(self) -> str:
        return f"glinet_binary_sensor/{self._hub.device_mac}/repeater_connected"

    @property
    def is_on(self) -> bool | None:
        return self._hub.repeater_connected

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        status = self._hub.repeater_status
        if status is None:
            return None
        attrs: dict[str, Any] = {}
        if status.ssid:
            attrs["ssid"] = status.ssid
        if status.bssid:
            attrs["bssid"] = status.bssid
        if status.signal is not None:
            attrs["signal"] = status.signal
        return attrs if attrs else None


class FanRunningBinarySensor(BinarySensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Fan status"
    _attr_translation_key = "fan_status"
    _attr_device_class = BinarySensorDeviceClass.RUNNING
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:fan"

    def __init__(self, hub: GLinetHub) -> None:
        self._hub = hub
        self._attr_device_info = hub.device_info

    @property
    def unique_id(self) -> str:
        return f"glinet_binary_sensor/{self._hub.device_mac}/fan_running"

    @property
    def is_on(self) -> bool | None:
        return self._hub.fan_running

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        attrs: dict[str, Any] = {}
        if self._hub.fan_speed is not None:
            attrs["speed"] = self._hub.fan_speed
        if self._hub.fan_temperature_threshold is not None:
            attrs["temperature_threshold"] = self._hub.fan_temperature_threshold
        return attrs if attrs else None


def _internet_is_connected(status: dict[str, Any]) -> bool | None:
    def _search(value: Any) -> bool | None:
        if isinstance(value, dict):
            for key, child in value.items():
                normalized = str(key).lower()
                if normalized in {"online", "connected", "internet", "up"}:
                    if isinstance(child, bool):
                        return child
                    if isinstance(child, int):
                        return child != 0
                    if isinstance(child, str):
                        lowered = child.lower()
                        if lowered in {"online", "connected", "up", "1", "true"}:
                            return True
                        if lowered in {"offline", "disconnected", "down", "0", "false"}:
                            return False
                if normalized in {"state", "status"} and isinstance(child, str):
                    lowered = child.lower()
                    if lowered in {"online", "connected", "up"}:
                        return True
                    if lowered in {"offline", "disconnected", "down"}:
                        return False
                nested = _search(child)
                if nested is not None:
                    return nested
        elif isinstance(value, list):
            for item in value:
                nested = _search(item)
                if nested is not None:
                    return nested
        return None

    return _search(status)
