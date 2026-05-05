from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.const import EntityCategory

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from ..hub import GLinetHub


async def async_setup_entry(
    _: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    hub: GLinetHub = entry.runtime_data
    async_add_entities([InternetStatusBinarySensor(hub)], True)


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
