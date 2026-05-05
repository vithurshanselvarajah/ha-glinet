from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.button import ButtonEntity
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
    async_add_entities(
        [RebootButton(hub)],
        True,
    )


class RebootButton(ButtonEntity):
    _attr_icon = "mdi:restart"
    _attr_has_entity_name = True

    def __init__(self, hub: GLinetHub) -> None:
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
        await self._hub.router_api.reboot_router()
