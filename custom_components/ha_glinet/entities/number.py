from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberMode
from homeassistant.const import EntityCategory, UnitOfTemperature

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from ..hub import GLinetHub

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    _: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    hub: GLinetHub = entry.runtime_data
    async_add_entities([FanTemperatureThresholdNumber(hub)], True)


class FanTemperatureThresholdNumber(NumberEntity):

    _attr_has_entity_name = True
    _attr_name = "Fan trigger temperature"
    _attr_icon = "mdi:thermometer-auto"
    _attr_device_class = NumberDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_native_min_value = 40
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, hub: GLinetHub) -> None:
        self._hub = hub
        self._attr_device_info = hub.device_info

    @property
    def unique_id(self) -> str:
        return f"glinet_number/{self._hub.device_mac}/fan_temperature"

    @property
    def native_value(self) -> float | None:
        return self._hub.fan_temperature_threshold

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        warn_temp = self._hub.fan_warn_temperature
        if warn_temp is not None:
            return {"factory_default": warn_temp}
        return None

    async def async_set_native_value(self, value: float) -> None:
        await self._hub.set_fan_temperature(int(value))
