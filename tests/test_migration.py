"""Tests for the legacy ha_glinet -> glinet_router config-entry migration."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from custom_components.glinet_router import (
    PLATFORMS,
    _migrate_legacy_entry,
)
from custom_components.glinet_router.const import DOMAIN, LEGACY_DOMAIN


class _FakeConfigEntries:
    """Minimal stand-in for ``hass.config_entries`` used by the migration."""

    def __init__(self) -> None:
        self.updates: list[tuple[Any, dict[str, Any]]] = []

    def async_update_entry(self, entry: Any, **changes: Any) -> None:
        for key, value in changes.items():
            setattr(entry, key, value)
        self.updates.append((entry, dict(changes)))


def _make_entry(domain: str) -> Any:
    return SimpleNamespace(
        entry_id="abc123",
        domain=domain,
        data={"host": "http://192.168.8.1", "password": "pw"},
        options={},
    )


async def test_migrate_legacy_entry_rekeys_to_new_domain() -> None:
    hass = SimpleNamespace(config_entries=_FakeConfigEntries())
    entry = _make_entry(LEGACY_DOMAIN)

    await _migrate_legacy_entry(hass, entry)

    assert entry.domain == DOMAIN
    assert hass.config_entries.updates == [(entry, {"domain": DOMAIN})]


async def test_migrate_legacy_entry_is_noop_for_new_domain() -> None:
    hass = SimpleNamespace(config_entries=_FakeConfigEntries())
    entry = _make_entry(DOMAIN)

    await _migrate_legacy_entry(hass, entry)

    assert hass.config_entries.updates == []


async def test_migrate_legacy_entry_is_noop_for_unrelated_domain() -> None:
    hass = SimpleNamespace(config_entries=_FakeConfigEntries())
    entry = _make_entry("some_other_domain")

    await _migrate_legacy_entry(hass, entry)

    assert hass.config_entries.updates == []
    assert entry.domain == "some_other_domain"


def test_platforms_are_subset_of_legacy_platforms() -> None:
    """The platform list must match between old and new integration.

    The hub construct and config-entry setup forward setups for every
    platform listed in ``PLATFORMS``. If a future change adds a new
    platform, the legacy migration list must be updated at the same
    time, otherwise users migrating from ``ha_glinet`` would lose
    entities on upgrade.
    """
    expected = {
        "binary_sensor",
        "button",
        "device_tracker",
        "select",
        "sensor",
        "switch",
        "update",
    }
    assert set(PLATFORMS) == expected


def test_domain_constants_are_stable() -> None:
    """The legacy domain constant must stay frozen once published.

    The migration relies on ``LEGACY_DOMAIN`` matching exactly what the
    previous integration wrote to the config-entry store. Changing this
    value would silently break the migration for users updating from
    the old integration.
    """
    assert LEGACY_DOMAIN == "ha_glinet"
    assert DOMAIN == "glinet_router"
    assert DOMAIN != LEGACY_DOMAIN
