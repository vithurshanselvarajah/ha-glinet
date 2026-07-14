from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from .const import DOMAIN, LEGACY_DOMAIN

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from .hub import GLinetHub

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [
    "binary_sensor",
    "button",
    "device_tracker",
    "select",
    "sensor",
    "switch",
    "update",
]


async def _migrate_legacy_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    if entry.domain == DOMAIN:
        return
    if entry.domain != LEGACY_DOMAIN:
        return

    _LOGGER.debug(
        "Re-keying in-place config entry %s from %s to %s",
        entry.entry_id,
        LEGACY_DOMAIN,
        DOMAIN,
    )
    hass.config_entries.async_update_entry(entry, domain=DOMAIN)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    from .hub import GLinetHub

    await _migrate_legacy_entry(hass, entry)

    hub = GLinetHub(hass, entry)
    await hub.async_initialize_hub()
    await hub.async_config_entry_first_refresh()
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
