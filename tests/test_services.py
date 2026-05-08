from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from custom_components.ha_glinet.const import (
    CONF_ENABLED_FEATURES,
    DOMAIN,
    FEATURE_REPEATER,
    FEATURE_SMS,
    SERVICE_CONNECT_WIFI,
    SERVICE_DISCONNECT_WIFI,
    SERVICE_GET_SAVED_NETWORKS,
    SERVICE_GET_SMS,
    SERVICE_REFRESH_SMS,
    SERVICE_REMOVE_SAVED_NETWORK,
    SERVICE_REMOVE_SMS,
    SERVICE_SCAN_WIFI,
    SERVICE_SEND_SMS,
    SERVICE_SET_FAN_TEMPERATURE,
)
from custom_components.ha_glinet.services import (
    _enabled_features_from_entry,
    async_register_services,
)


class DummyServices:
    def __init__(self) -> None:
        self.registrations: list[tuple[str, dict[str, Any]]] = []

    def async_register(self, domain: str, service: str, handler: Any, **kwargs: Any) -> None:
        self.registrations.append((service, kwargs))

    def has_service(self, domain: str, service: str) -> bool:
        return any(s == service for s, _ in self.registrations)

    def async_remove(self, domain: str, service: str) -> None:
        self.registrations = [(s, k) for s, k in self.registrations if s != service]



class DummyHass:
    def __init__(self, entries: list[Any]) -> None:
        self.config_entries = SimpleNamespace(async_entries=lambda domain: entries)
        self.services = DummyServices()


class DummyEntry:
    def __init__(
        self, data: dict[str, Any] | None = None, options: dict[str, Any] | None = None
    ) -> None:
        self.data = data or {}
        self.options = options or {}
        self.runtime_data = None


async def test_register_services_removes_services_when_feature_is_disabled() -> None:
    entry = DummyEntry(data={CONF_ENABLED_FEATURES: [FEATURE_SMS]})
    hass = DummyHass([entry])
    await async_register_services(hass)
    assert hass.services.has_service(DOMAIN, SERVICE_SEND_SMS)

    entry.data[CONF_ENABLED_FEATURES] = []
    await async_register_services(hass)

    assert not hass.services.has_service(DOMAIN, SERVICE_SEND_SMS)


async def test_enabled_features_from_entry_uses_default_options_when_missing() -> None:
    entry = DummyEntry()

    enabled = _enabled_features_from_entry(entry)

    assert FEATURE_SMS in enabled
    assert FEATURE_REPEATER in enabled


async def test_register_services_records_only_enabled_feature_services() -> None:
    entry = DummyEntry(data={CONF_ENABLED_FEATURES: [FEATURE_SMS, FEATURE_REPEATER]})
    hass = DummyHass([entry])

    await async_register_services(hass)

    registered = {service for service, _ in hass.services.registrations}
    assert registered == {
        SERVICE_SEND_SMS,
        SERVICE_REFRESH_SMS,
        SERVICE_GET_SMS,
        SERVICE_REMOVE_SMS,
        SERVICE_SCAN_WIFI,
        SERVICE_CONNECT_WIFI,
        SERVICE_DISCONNECT_WIFI,
        SERVICE_GET_SAVED_NETWORKS,
        SERVICE_REMOVE_SAVED_NETWORK,
        SERVICE_SET_FAN_TEMPERATURE,
    }


async def test_register_services_skips_disabled_features() -> None:
    entry = DummyEntry(data={CONF_ENABLED_FEATURES: []})
    hass = DummyHass([entry])

    await async_register_services(hass)

    assert hass.services.has_service(DOMAIN, SERVICE_SET_FAN_TEMPERATURE)
    assert [s for s, _ in hass.services.registrations if s != SERVICE_SET_FAN_TEMPERATURE] == []


async def test_register_services_does_not_register_repeater_when_not_enabled() -> None:
    entry = DummyEntry(data={CONF_ENABLED_FEATURES: [FEATURE_SMS]})
    hass = DummyHass([entry])

    await async_register_services(hass)

    registered = {service for service, _ in hass.services.registrations}
    assert SERVICE_SCAN_WIFI not in registered
    assert SERVICE_CONNECT_WIFI not in registered
    assert SERVICE_DISCONNECT_WIFI not in registered
    assert SERVICE_GET_SAVED_NETWORKS not in registered
    assert SERVICE_REMOVE_SAVED_NETWORK not in registered
