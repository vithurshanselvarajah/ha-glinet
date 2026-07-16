from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from custom_components.glinet_router.const import (
    ATTR_ALL_BAND,
    ATTR_BLOCK,
    ATTR_BODY,
    ATTR_BSSID,
    ATTR_CONFIG,
    ATTR_DEST,
    ATTR_DEST_IP,
    ATTR_DEST_PORT,
    ATTR_DFS,
    ATTR_ENABLED,
    ATTR_GROUP_ID,
    ATTR_INTERFACE,
    ATTR_METHOD,
    ATTR_MODE,
    ATTR_NAME,
    ATTR_PASSWORD,
    ATTR_PROTO,
    ATTR_REFRESH,
    ATTR_REMEMBER,
    ATTR_REMOVE_ALL,
    ATTR_RULE_ID,
    ATTR_SENSITIVITY,
    ATTR_SRC,
    ATTR_SRC_DPORT,
    ATTR_SRC_MAC,
    ATTR_SSID,
    CONF_ENABLED_FEATURES,
    DOMAIN,
    FEATURE_FIREWALL,
    FEATURE_KMWAN,
    FEATURE_MWAN3,
    FEATURE_PARENTAL_CONTROL,
    FEATURE_PLAYGROUND,
    FEATURE_REPEATER,
    FEATURE_SMS,
    SERVICE_ACCESS_CONTROL_SET_DEVICE_BLOCK,
    SERVICE_ACCESS_CONTROL_SET_MODE,
    SERVICE_ADD_FIREWALL_RULE,
    SERVICE_ADD_PORT_FORWARD,
    SERVICE_CONNECT_WIFI,
    SERVICE_DISCONNECT_WIFI,
    SERVICE_GET_SAVED_NETWORKS,
    SERVICE_GET_SMS,
    SERVICE_KMWAN_GET_CONFIG,
    SERVICE_KMWAN_GET_STATUS,
    SERVICE_KMWAN_SET_CONFIG,
    SERVICE_KMWAN_SET_INTERFACE,
    SERVICE_KMWAN_SET_SENSITIVITY,
    SERVICE_MWAN3_GET_CONFIG,
    SERVICE_MWAN3_GET_STATUS,
    SERVICE_MWAN3_SET_CONFIG,
    SERVICE_MWAN3_SET_INTERFACE,
    SERVICE_PARENTAL_CONTROL_SET_FILTERING_MODE,
    SERVICE_PARENTAL_CONTROL_SET_GROUP_SCHEDULES,
    SERVICE_PARENTAL_CONTROL_SET_TEMPORARY_OVERRIDE,
    SERVICE_PARENTAL_CONTROL_UPDATE_SIGNATURES,
    SERVICE_PLAYGROUND,
    SERVICE_REFRESH_CLIENTS,
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
from custom_components.glinet_router.services import (
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


async def test_register_services_removes_repeater_actions_when_feature_is_disabled() -> None:
    entry = DummyEntry(data={CONF_ENABLED_FEATURES: [FEATURE_REPEATER]})
    hass = DummyHass([entry])
    await async_register_services(hass)
    assert hass.services.has_service(DOMAIN, SERVICE_SCAN_WIFI)
    assert hass.services.has_service(DOMAIN, SERVICE_CONNECT_WIFI)
    assert hass.services.has_service(DOMAIN, SERVICE_DISCONNECT_WIFI)
    assert hass.services.has_service(DOMAIN, SERVICE_GET_SAVED_NETWORKS)
    assert hass.services.has_service(DOMAIN, SERVICE_REMOVE_SAVED_NETWORK)

    entry.data[CONF_ENABLED_FEATURES] = []
    await async_register_services(hass)

    assert not hass.services.has_service(DOMAIN, SERVICE_SCAN_WIFI)
    assert not hass.services.has_service(DOMAIN, SERVICE_CONNECT_WIFI)
    assert not hass.services.has_service(DOMAIN, SERVICE_DISCONNECT_WIFI)
    assert not hass.services.has_service(DOMAIN, SERVICE_GET_SAVED_NETWORKS)
    assert not hass.services.has_service(DOMAIN, SERVICE_REMOVE_SAVED_NETWORK)


async def test_register_services_removes_parental_services_when_feature_is_disabled() -> None:
    entry = DummyEntry(data={CONF_ENABLED_FEATURES: [FEATURE_PARENTAL_CONTROL]})
    hass = DummyHass([entry])
    await async_register_services(hass)
    assert hass.services.has_service(
        DOMAIN,
        SERVICE_PARENTAL_CONTROL_SET_TEMPORARY_OVERRIDE,
    )

    entry.data[CONF_ENABLED_FEATURES] = []
    await async_register_services(hass)

    assert not hass.services.has_service(
        DOMAIN,
        SERVICE_PARENTAL_CONTROL_SET_TEMPORARY_OVERRIDE,
    )
    assert not hass.services.has_service(DOMAIN, SERVICE_ACCESS_CONTROL_SET_MODE)
    assert not hass.services.has_service(DOMAIN, SERVICE_ACCESS_CONTROL_SET_DEVICE_BLOCK)


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
        SERVICE_REFRESH_CLIENTS,
    }


async def test_register_services_records_mwan3_services_when_enabled() -> None:
    entry = DummyEntry(data={CONF_ENABLED_FEATURES: [FEATURE_MWAN3]})
    hass = DummyHass([entry])

    await async_register_services(hass)

    registered = {service for service, _ in hass.services.registrations}
    assert SERVICE_MWAN3_GET_CONFIG in registered
    assert SERVICE_MWAN3_GET_STATUS in registered
    assert SERVICE_MWAN3_SET_CONFIG in registered
    assert SERVICE_MWAN3_SET_INTERFACE in registered


async def test_register_services_removes_mwan3_services_when_feature_is_disabled() -> None:
    entry = DummyEntry(data={CONF_ENABLED_FEATURES: [FEATURE_MWAN3]})
    hass = DummyHass([entry])
    await async_register_services(hass)
    assert hass.services.has_service(DOMAIN, SERVICE_MWAN3_GET_CONFIG)

    entry.data[CONF_ENABLED_FEATURES] = []
    await async_register_services(hass)

    assert not hass.services.has_service(DOMAIN, SERVICE_MWAN3_GET_CONFIG)
    assert not hass.services.has_service(DOMAIN, SERVICE_MWAN3_GET_STATUS)
    assert not hass.services.has_service(DOMAIN, SERVICE_MWAN3_SET_CONFIG)
    assert not hass.services.has_service(DOMAIN, SERVICE_MWAN3_SET_INTERFACE)


async def test_mwan3_service_handlers_call_hub_methods() -> None:
    calls: list[tuple[str, Any]] = []

    class Hub:
        device_mac = "00:11:22:33:44:55"

        def feature_enabled(self, feature: str) -> bool:
            return feature == FEATURE_MWAN3

        async def get_mwan3_config(self) -> dict[str, Any]:
            calls.append(("get_config", None))
            return {"mode": 1}

        async def get_mwan3_status(self) -> dict[str, Any]:
            calls.append(("get_status", None))
            return {"interfaces": []}

        async def set_mwan3_config(self, config: dict[str, Any]) -> None:
            calls.append(("set_config", config))

        async def set_mwan3_interface(self, interface: dict[str, Any]) -> None:
            calls.append(("set_interface", interface))

    entry = DummyEntry(data={CONF_ENABLED_FEATURES: [FEATURE_MWAN3]})
    entry.runtime_data = Hub()
    hass = DummyHass([entry])
    await async_register_services(hass)

    assert await hass.services.handlers[SERVICE_MWAN3_GET_CONFIG](SimpleNamespace(data={})) == {
        "config": {"mode": 1}
    }
    assert await hass.services.handlers[SERVICE_MWAN3_GET_STATUS](SimpleNamespace(data={})) == {
        "status": {"interfaces": []}
    }
    await hass.services.handlers[SERVICE_MWAN3_SET_CONFIG](
        SimpleNamespace(data={ATTR_CONFIG: {"mode": 0, "interfaces": []}})
    )
    await hass.services.handlers[SERVICE_MWAN3_SET_INTERFACE](
        SimpleNamespace(data={ATTR_INTERFACE: {"interface": "wan", "enable_check": True}})
    )

    assert calls == [
        ("get_config", None),
        ("get_status", None),
        ("set_config", {"mode": 0, "interfaces": []}),
        ("set_interface", {"interface": "wan", "enable_check": True}),
    ]


async def test_register_services_records_kmwan_services_when_enabled() -> None:
    entry = DummyEntry(data={CONF_ENABLED_FEATURES: [FEATURE_KMWAN]})
    hass = DummyHass([entry])

    await async_register_services(hass)

    registered = {service for service, _ in hass.services.registrations}
    assert SERVICE_KMWAN_GET_CONFIG in registered
    assert SERVICE_KMWAN_GET_STATUS in registered
    assert SERVICE_KMWAN_SET_CONFIG in registered
    assert SERVICE_KMWAN_SET_INTERFACE in registered
    assert SERVICE_KMWAN_SET_SENSITIVITY in registered


async def test_register_services_removes_kmwan_services_when_feature_is_disabled() -> None:
    entry = DummyEntry(data={CONF_ENABLED_FEATURES: [FEATURE_KMWAN]})
    hass = DummyHass([entry])
    await async_register_services(hass)
    assert hass.services.has_service(DOMAIN, SERVICE_KMWAN_GET_CONFIG)

    entry.data[CONF_ENABLED_FEATURES] = []
    await async_register_services(hass)

    assert not hass.services.has_service(DOMAIN, SERVICE_KMWAN_GET_CONFIG)
    assert not hass.services.has_service(DOMAIN, SERVICE_KMWAN_GET_STATUS)
    assert not hass.services.has_service(DOMAIN, SERVICE_KMWAN_SET_CONFIG)
    assert not hass.services.has_service(DOMAIN, SERVICE_KMWAN_SET_INTERFACE)
    assert not hass.services.has_service(DOMAIN, SERVICE_KMWAN_SET_SENSITIVITY)


async def test_kmwan_service_handlers_call_hub_methods() -> None:
    calls: list[tuple[str, Any]] = []

    class Hub:
        device_mac = "00:11:22:33:44:55"

        def feature_enabled(self, feature: str) -> bool:
            return feature == FEATURE_KMWAN

        async def get_kmwan_config(self) -> dict[str, Any]:
            calls.append(("get_config", None))
            return {"mode": 1}

        async def get_kmwan_status(self) -> dict[str, Any]:
            calls.append(("get_status", None))
            return {"interfaces": []}

        async def set_kmwan_config(self, config: dict[str, Any]) -> None:
            calls.append(("set_config", config))

        async def set_kmwan_interface(self, interface: dict[str, Any]) -> None:
            calls.append(("set_interface", interface))

        async def set_kmwan_sensitivity(self, sensitivity: dict[str, Any]) -> None:
            calls.append(("set_sensitivity", sensitivity))

    entry = DummyEntry(data={CONF_ENABLED_FEATURES: [FEATURE_KMWAN]})
    entry.runtime_data = Hub()
    hass = DummyHass([entry])
    await async_register_services(hass)

    assert await hass.services.handlers[SERVICE_KMWAN_GET_CONFIG](SimpleNamespace(data={})) == {
        "config": {"mode": 1}
    }
    assert await hass.services.handlers[SERVICE_KMWAN_GET_STATUS](SimpleNamespace(data={})) == {
        "status": {"interfaces": []}
    }
    await hass.services.handlers[SERVICE_KMWAN_SET_CONFIG](
        SimpleNamespace(data={ATTR_CONFIG: {"mode": 0, "interfaces": []}})
    )
    await hass.services.handlers[SERVICE_KMWAN_SET_INTERFACE](
        SimpleNamespace(data={ATTR_INTERFACE: {"interface": "wan", "enable_check": True}})
    )
    await hass.services.handlers[SERVICE_KMWAN_SET_SENSITIVITY](
        SimpleNamespace(data={ATTR_SENSITIVITY: {"level": "custom", "val": 5}})
    )

    assert calls == [
        ("get_config", None),
        ("get_status", None),
        ("set_config", {"mode": 0, "interfaces": []}),
        ("set_interface", {"interface": "wan", "enable_check": True}),
        ("set_sensitivity", {"level": "custom", "val": 5}),
    ]


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


async def test_register_services_records_parental_control_services_when_enabled() -> None:
    entry = DummyEntry(data={CONF_ENABLED_FEATURES: [FEATURE_PARENTAL_CONTROL]})
    hass = DummyHass([entry])

    await async_register_services(hass)

    registered = {service for service, _ in hass.services.registrations}
    assert SERVICE_PARENTAL_CONTROL_SET_TEMPORARY_OVERRIDE in registered
    assert SERVICE_PARENTAL_CONTROL_SET_FILTERING_MODE in registered
    assert SERVICE_PARENTAL_CONTROL_UPDATE_SIGNATURES in registered
    assert SERVICE_ACCESS_CONTROL_SET_MODE in registered
    assert SERVICE_ACCESS_CONTROL_SET_DEVICE_BLOCK in registered
    assert SERVICE_PARENTAL_CONTROL_SET_GROUP_SCHEDULES in registered


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


async def test_parental_control_service_handlers_call_hub_methods() -> None:
    calls: list[tuple[str, Any]] = []

    class Hub:
        device_mac = "00:11:22:33:44:55"

        def feature_enabled(self, feature: str) -> bool:
            return feature == FEATURE_PARENTAL_CONTROL

        async def set_temporary_override(
            self,
            group_id: str,
            enable: bool,
            duration: str,
            rule_id: str,
        ) -> None:
            calls.append(("temporary_override", group_id, enable, duration, rule_id))

        async def set_parental_mode(self, mode: int) -> None:
            calls.append(("parental_mode", mode))

        async def update_parental_signatures(self) -> None:
            calls.append(("update_signatures", None))

        async def set_access_control_mode(self, mode: str) -> None:
            calls.append(("access_mode", mode))

        async def set_single_device_block(self, mac: str, block: bool) -> None:
            calls.append(("device_block", mac, block))

        async def set_group_schedules_enabled(
            self,
            group_id: str,
            enabled: bool,
        ) -> None:
            calls.append(("group_schedules", group_id, enabled))

    entry = DummyEntry(data={CONF_ENABLED_FEATURES: [FEATURE_PARENTAL_CONTROL]})
    entry.runtime_data = Hub()
    hass = DummyHass([entry])
    await async_register_services(hass)

    await hass.services.handlers[SERVICE_PARENTAL_CONTROL_SET_TEMPORARY_OVERRIDE](
        SimpleNamespace(
            data={
                ATTR_GROUP_ID: "group1",
                ATTR_ENABLED: True,
                ATTR_RULE_ID: "drop",
            }
        )
    )
    await hass.services.handlers[SERVICE_PARENTAL_CONTROL_SET_FILTERING_MODE](
        SimpleNamespace(data={ATTR_MODE: 1})
    )
    await hass.services.handlers[SERVICE_PARENTAL_CONTROL_UPDATE_SIGNATURES](
        SimpleNamespace(data={})
    )
    await hass.services.handlers[SERVICE_ACCESS_CONTROL_SET_MODE](
        SimpleNamespace(data={ATTR_MODE: "black"})
    )
    await hass.services.handlers[SERVICE_ACCESS_CONTROL_SET_DEVICE_BLOCK](
        SimpleNamespace(data={ATTR_SRC_MAC: "aa:bb", ATTR_BLOCK: True})
    )
    await hass.services.handlers[SERVICE_PARENTAL_CONTROL_SET_GROUP_SCHEDULES](
        SimpleNamespace(data={ATTR_GROUP_ID: "group1", ATTR_ENABLED: False})
    )

    assert calls == [
        ("temporary_override", "group1", True, "", "drop"),
        ("parental_mode", 1),
        ("update_signatures", None),
        ("access_mode", "black"),
        ("device_block", "aa:bb", True),
        ("group_schedules", "group1", False),
    ]


async def test_register_services_skips_disabled_features() -> None:
    entry = DummyEntry(data={CONF_ENABLED_FEATURES: []})
    hass = DummyHass([entry])

    await async_register_services(hass)

    assert hass.services.has_service(DOMAIN, SERVICE_SET_FAN_TEMPERATURE)
    assert hass.services.has_service(DOMAIN, SERVICE_REFRESH_CLIENTS)
    core_services = {SERVICE_SET_FAN_TEMPERATURE, SERVICE_REFRESH_CLIENTS}
    assert [s for s, _ in hass.services.registrations if s not in core_services] == []


async def test_repeater_scan_action_passes_refresh_flags() -> None:
    calls: list[tuple[str, Any]] = []

    class Hub:
        device_mac = "00:11:22:33:44:55"

        def feature_enabled(self, feature: str) -> bool:
            return feature == FEATURE_REPEATER

        async def scan_wifi_networks(
            self,
            all_band: bool = False,
            dfs: bool = False,
            refresh: bool = False,
        ) -> list[Any]:
            calls.append(("scan", {"all_band": all_band, "dfs": dfs, "refresh": refresh}))
            return []

    entry = DummyEntry(data={CONF_ENABLED_FEATURES: [FEATURE_REPEATER]})
    entry.runtime_data = Hub()
    hass = DummyHass([entry])
    await async_register_services(hass)

    response = await hass.services.handlers[SERVICE_SCAN_WIFI](
        SimpleNamespace(data={ATTR_ALL_BAND: True, ATTR_DFS: True, ATTR_REFRESH: True})
    )

    assert calls == [("scan", {"all_band": True, "dfs": True, "refresh": True})]
    assert response == {"networks": []}


async def test_repeater_connect_action_passes_secured_network_password() -> None:
    calls: list[tuple[str, Any]] = []

    class Hub:
        device_mac = "00:11:22:33:44:55"

        def feature_enabled(self, feature: str) -> bool:
            return feature == FEATURE_REPEATER

        async def connect_to_wifi(
            self,
            ssid: str,
            password: str | None = None,
            remember: bool = True,
            bssid: str | None = None,
        ) -> None:
            calls.append(
                (
                    "connect",
                    {
                        "ssid": ssid,
                        "password": password,
                        "remember": remember,
                        "bssid": bssid,
                    },
                )
            )

    entry = DummyEntry(data={CONF_ENABLED_FEATURES: [FEATURE_REPEATER]})
    entry.runtime_data = Hub()
    hass = DummyHass([entry])
    await async_register_services(hass)

    await hass.services.handlers[SERVICE_CONNECT_WIFI](
        SimpleNamespace(
            data={
                ATTR_SSID: "SecuredNet",
                ATTR_PASSWORD: "secret-pass",
                ATTR_REMEMBER: False,
                ATTR_BSSID: "00:11:22:33:44:55",
            }
        )
    )

    assert calls == [
        (
            "connect",
            {
                "ssid": "SecuredNet",
                "password": "secret-pass",
                "remember": False,
                "bssid": "00:11:22:33:44:55",
            },
        )
    ]


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


async def test_register_services_records_playground_service_when_enabled() -> None:
    entry = DummyEntry(data={CONF_ENABLED_FEATURES: [FEATURE_PLAYGROUND]})
    hass = DummyHass([entry])

    await async_register_services(hass)

    registered = {service for service, _ in hass.services.registrations}
    assert SERVICE_PLAYGROUND in registered


async def test_register_services_removes_playground_service_when_disabled() -> None:
    entry = DummyEntry(data={CONF_ENABLED_FEATURES: [FEATURE_PLAYGROUND]})
    hass = DummyHass([entry])
    await async_register_services(hass)
    assert hass.services.has_service(DOMAIN, SERVICE_PLAYGROUND)

    entry.data[CONF_ENABLED_FEATURES] = []
    await async_register_services(hass)

    assert not hass.services.has_service(DOMAIN, SERVICE_PLAYGROUND)


async def test_playground_service_handler_calls_hub_method() -> None:
    calls = []

    class Hub:
        device_mac = "00:11:22:33:44:55"

        def feature_enabled(self, feature: str) -> bool:
            return feature == FEATURE_PLAYGROUND

        async def custom_request(
            self,
            method: str,
            body: dict[str, Any] | list[Any] | None = None,
        ) -> dict[str, Any] | list[Any] | None:
            calls.append((method, body))
            return {"status": "ok"}

    entry = DummyEntry(data={CONF_ENABLED_FEATURES: [FEATURE_PLAYGROUND]})
    entry.runtime_data = Hub()
    hass = DummyHass([entry])
    await async_register_services(hass)

    response = await hass.services.handlers[SERVICE_PLAYGROUND](
        SimpleNamespace(data={ATTR_METHOD: "system/get_info", ATTR_BODY: {"test": 1}})
    )

    assert calls == [("system/get_info", {"test": 1})]
    assert response == {"status": "ok"}


async def test_refresh_clients_service_handler_calls_hub_methods() -> None:
    calls: list[tuple[str, Any]] = []

    class Hub:
        device_mac = "00:11:22:33:44:55"

        async def fetch_connected_devices(self) -> None:
            calls.append(("fetch_connected_devices", None))

        async def async_request_refresh(self) -> None:
            calls.append(("async_request_refresh", None))

    entry = DummyEntry()
    entry.runtime_data = Hub()
    hass = DummyHass([entry])
    await async_register_services(hass)

    await hass.services.handlers[SERVICE_REFRESH_CLIENTS](SimpleNamespace(data={}))

    assert calls == [
        ("fetch_connected_devices", None),
        ("async_request_refresh", None),
    ]
