from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.device_tracker import SourceType
from homeassistant.components.device_tracker.config_entry import ScannerEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

    from ..hub import GLinetHub
    from ..models import ClientDeviceInfo

DEFAULT_DEVICE_NAME = "Unknown device"


async def async_setup_entry(
    _: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    hub: GLinetHub = entry.runtime_data
    tracked: set[str] = set()

    @callback
    def register_new_devices() -> None:
        new_entities = [
            GLinetDevice(hub, device)
            for mac, device in hub.tracked_devices.items()
            if mac not in tracked
        ]
        for entity in new_entities:
            tracked.add(entity.unique_id)
        if new_entities:
            async_add_entities(new_entities)

    register_new_devices()
    entry.async_on_unload(
        async_dispatcher_connect(hub.hass, hub.event_device_added, register_new_devices)
    )


class GLinetDevice(ScannerEntity):
    _attr_source_type = SourceType.ROUTER
    _attr_icon = "mdi:radar"
    _attr_should_poll = False

    def __init__(self, hub: GLinetHub, device: ClientDeviceInfo) -> None:
        self._hub = hub
        self._device = device
        self._attr_unique_id = device.mac
        self._attr_hostname = device.name or DEFAULT_DEVICE_NAME
        self._attr_name = self._attr_hostname
        self._attr_ip_address = device.ip_address
        self._attr_mac_address = device.mac

    @property
    def is_connected(self) -> bool:
        return self._device.is_connected

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        attributes: dict[str, Any] = {"interface_type": str(self._device.interface_type)}
        if self._device.last_activity:
            attributes["last_time_reachable"] = self._device.last_activity.isoformat(
                timespec="seconds"
            )
        return attributes

    @callback
    def _on_router_data_updated(self) -> None:
        self._device = self._hub.tracked_devices[self._device.mac]
        self._attr_hostname = self._device.name or DEFAULT_DEVICE_NAME
        self._attr_name = self._attr_hostname
        self._attr_ip_address = self._device.ip_address
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                self._hub.event_device_updated,
                self._on_router_data_updated,
            )
        )
