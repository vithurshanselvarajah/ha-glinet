from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from custom_components.ha_glinet.const import (
    ATTR_DEST,
    ATTR_DEST_IP,
    ATTR_DEST_PORT,
    ATTR_ENABLED,
    ATTR_NAME,
    ATTR_PROTO,
    ATTR_REMOVE_ALL,
    ATTR_RULE_ID,
    ATTR_SRC,
    ATTR_SRC_DPORT,
    CONF_ENABLED_FEATURES,
    DOMAIN,
    FEATURE_FIREWALL,
    FEATURE_REPEATER,
    FEATURE_SMS,
    SERVICE_ADD_FIREWALL_RULE,
    SERVICE_ADD_PORT_FORWARD,
    SERVICE_CONNECT_WIFI,
    SERVICE_DISCONNECT_WIFI,
    SERVICE_GET_SAVED_NETWORKS,
    SERVICE_GET_SMS,
    SERVICE_REFRESH_SMS,
    SERVICE_REMOVE_FIREWALL_RULE,
    SERVICE_REMOVE_PORT_FORWARD,
    SERVICE_REMOVE_SAVED_NETWORK,
    SERVICE_REMOVE_SMS,
    SERVICE_SCAN_WIFI,
    SERVICE_SEND_SMS,
    SERVICE_SET_DMZ,
    SERVICE_SET_FAN_TEMPERATURE,
)
from custom_components.ha_glinet.services import (
    _enabled_features_from_entry,
    async_register_services,
)


class DummyServices:
    def __init__(self) -> None:
        self.registrations: list[tuple[str, dict[str, Any]]] = []
        self.handlers: dict[str, Any] = {}

    def async_register(self, domain: str, service: str, handler: Any, **kwargs: Any) -> None:
        self.registrations.append((service, kwargs))
        self.handlers[service] = handler

    def has_service(self, domain: str, service: str) -> bool:
        return any(s == service for s, _ in self.registrations)

    def async_remove(self, domain: str, service: str) -> None:
        self.registrations = [(s, k) for s, k in self.registrations if s != service]
        self.handlers.pop(service, None)



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


async def test_register_services_records_firewall_services_when_enabled() -> None:
    entry = DummyEntry(data={CONF_ENABLED_FEATURES: [FEATURE_FIREWALL]})
    hass = DummyHass([entry])

    await async_register_services(hass)

    registered = {service for service, _ in hass.services.registrations}
    assert SERVICE_ADD_FIREWALL_RULE in registered
    assert SERVICE_REMOVE_FIREWALL_RULE in registered
    assert SERVICE_ADD_PORT_FORWARD in registered
    assert SERVICE_REMOVE_PORT_FORWARD in registered
    assert SERVICE_SET_DMZ in registered


async def test_firewall_service_handlers_call_hub_methods() -> None:
    calls: list[tuple[str, Any]] = []

    class Hub:
        device_mac = "00:11:22:33:44:55"

        def feature_enabled(self, feature: str) -> bool:
            return feature == FEATURE_FIREWALL

        async def add_firewall_rule(self, params: dict[str, Any]) -> None:
            calls.append(("add_firewall_rule", params))

        async def remove_firewall_rule(
            self,
            rule_id: str | None = None,
            remove_all: bool = False,
        ) -> None:
            calls.append(("remove_firewall_rule", (rule_id, remove_all)))

        async def add_port_forward(self, params: dict[str, Any]) -> None:
            calls.append(("add_port_forward", params))

        async def remove_port_forward(
            self,
            rule_id: str | None = None,
            remove_all: bool = False,
        ) -> None:
            calls.append(("remove_port_forward", (rule_id, remove_all)))

        async def set_dmz_config(
            self,
            enabled: bool,
            dest_ip: str | None = None,
        ) -> None:
            calls.append(("set_dmz_config", (enabled, dest_ip)))

    entry = DummyEntry(data={CONF_ENABLED_FEATURES: [FEATURE_FIREWALL]})
    entry.runtime_data = Hub()
    hass = DummyHass([entry])
    await async_register_services(hass)

    await hass.services.handlers[SERVICE_ADD_FIREWALL_RULE](
        SimpleNamespace(
            data={
                ATTR_NAME: "Allow SSH",
                ATTR_SRC: "wan",
                ATTR_PROTO: "tcp",
                ATTR_DEST: "lan",
                ATTR_DEST_PORT: "22",
                ATTR_ENABLED: True,
            }
        )
    )
    await hass.services.handlers[SERVICE_REMOVE_FIREWALL_RULE](
        SimpleNamespace(data={ATTR_RULE_ID: "rule-1"})
    )
    await hass.services.handlers[SERVICE_ADD_PORT_FORWARD](
        SimpleNamespace(
            data={
                ATTR_NAME: "Web",
                ATTR_SRC: "wan",
                ATTR_SRC_DPORT: "8443",
                ATTR_PROTO: "tcp",
                ATTR_DEST: "lan",
                ATTR_DEST_IP: "192.168.8.50",
                ATTR_DEST_PORT: "443",
            }
        )
    )
    await hass.services.handlers[SERVICE_REMOVE_PORT_FORWARD](
        SimpleNamespace(data={ATTR_REMOVE_ALL: True})
    )
    await hass.services.handlers[SERVICE_SET_DMZ](
        SimpleNamespace(data={ATTR_ENABLED: True, ATTR_DEST_IP: "192.168.8.50"})
    )

    assert calls == [
        (
            "add_firewall_rule",
            {
                ATTR_NAME: "Allow SSH",
                ATTR_SRC: "wan",
                ATTR_PROTO: "tcp",
                ATTR_DEST: "lan",
                ATTR_DEST_PORT: "22",
                ATTR_ENABLED: True,
            },
        ),
        ("remove_firewall_rule", ("rule-1", False)),
        (
            "add_port_forward",
            {
                ATTR_NAME: "Web",
                ATTR_SRC: "wan",
                ATTR_SRC_DPORT: "8443",
                ATTR_PROTO: "tcp",
                ATTR_DEST: "lan",
                ATTR_DEST_IP: "192.168.8.50",
                ATTR_DEST_PORT: "443",
            },
        ),
        ("remove_port_forward", (None, True)),
        ("set_dmz_config", (True, "192.168.8.50")),
    ]


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
