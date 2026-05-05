from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from .hub import GLinetHub

PLATFORMS = ["button", "device_tracker", "sensor", "switch"]


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    from .hub import GLinetHub

    hub = GLinetHub(hass, entry)
    await hub.async_initialize_hub()
    entry.runtime_data = hub
    entry.async_on_unload(entry.add_update_listener(handle_options_update))
    from .services import async_register_services

    await async_register_services(hass)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def handle_options_update(hass: HomeAssistant, entry: ConfigEntry) -> None:
    hub: GLinetHub = entry.runtime_data
    if hub.apply_option_updates(dict(entry.options)):
        await hass.config_entries.async_reload(entry.entry_id)
