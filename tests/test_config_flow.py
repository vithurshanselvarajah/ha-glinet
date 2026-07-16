from __future__ import annotations

import types
from typing import Any

from custom_components.glinet_router.config_flow import (
    CONF_ENABLED_FEATURES,
    DEFAULT_ENABLED_FEATURES,
    FEATURE_OPTIONS,
    SetupHub,
    _wan_monitor_options,
    process_user_input,
)
from custom_components.glinet_router.const import (
    CONF_PARALLEL_REQUESTS,
    CONF_WAN_STATUS_MONITORS,
    DEFAULT_PARALLEL_REQUESTS,
    DEFAULT_USERNAME,
    FEATURE_KMWAN,
    FEATURE_MWAN3,
    FEATURE_REPEATER,
    FEATURE_WG_CLIENT,
)


async def test_process_user_input_stores_enabled_features(monkeypatch) -> None:
    def fake_init(self, host: str, hass: Any, verify_ssl: bool = True) -> None:
        self.host = host
        self.username = DEFAULT_USERNAME
        self.router_mac = "00:00:00:00:00:00"
        self.router_model = "mr200"
        self.wan_interfaces = ["wan", "wwan"]

    async def fake_check_reachable(self) -> bool:
        return True

    async def fake_attempt_login(self, password: str) -> bool:
        return True

    monkeypatch.setattr(SetupHub, "__init__", fake_init)
    monkeypatch.setattr(SetupHub, "check_reachable", fake_check_reachable)
    monkeypatch.setattr(SetupHub, "attempt_login", fake_attempt_login)

    result = await process_user_input(
        {
            "host": "http://router",
            "password": "secret",
            CONF_ENABLED_FEATURES: [FEATURE_REPEATER],
        },
        types.SimpleNamespace(),
    )

    assert result["data"][CONF_ENABLED_FEATURES] == [FEATURE_REPEATER]
    assert result["data"][CONF_WAN_STATUS_MONITORS] == [
        "wan:ipv4",
        "wan:ipv6",
        "wwan:ipv4",
        "wwan:ipv6",
    ]


async def test_process_user_input_defaults_enabled_features_when_missing(monkeypatch) -> None:
    def fake_init(self, host: str, hass: Any, verify_ssl: bool = True) -> None:
        self.host = host
        self.username = DEFAULT_USERNAME
        self.router_mac = "00:00:00:00:00:00"
        self.router_model = "mr200"
        self.wan_interfaces = ["wan"]

    async def fake_check_reachable(self) -> bool:
        return True

    async def fake_attempt_login(self, password: str) -> bool:
        return True

    monkeypatch.setattr(SetupHub, "__init__", fake_init)
    monkeypatch.setattr(SetupHub, "check_reachable", fake_check_reachable)
    monkeypatch.setattr(SetupHub, "attempt_login", fake_attempt_login)

    result = await process_user_input(
        {"host": "http://router", "password": "secret"},
        types.SimpleNamespace(),
    )

    assert result["data"][CONF_ENABLED_FEATURES] == DEFAULT_ENABLED_FEATURES
    assert FEATURE_WG_CLIENT in result["data"][CONF_ENABLED_FEATURES]
    assert FEATURE_KMWAN not in result["data"][CONF_ENABLED_FEATURES]
    assert FEATURE_MWAN3 not in result["data"][CONF_ENABLED_FEATURES]
    assert result["data"][CONF_WAN_STATUS_MONITORS] == ["wan:ipv4", "wan:ipv6"]


def test_feature_options_include_kmwan_and_mwan3_labels() -> None:
    labels = {option["value"]: option["label"] for option in FEATURE_OPTIONS}

    assert labels["kmwan"] == "KMWan"
    assert labels["mwan3"] == "MWan3"


def test_wan_monitor_options_use_friendly_known_interface_names() -> None:
    assert _wan_monitor_options(["wan", "wwan", "modem_0001", "custom_wan"]) == [
        {"label": "Ethernet 1 IPv4", "value": "wan:ipv4"},
        {"label": "Ethernet 1 IPv6", "value": "wan:ipv6"},
        {"label": "Repeater IPv4", "value": "wwan:ipv4"},
        {"label": "Repeater IPv6", "value": "wwan:ipv6"},
        {"label": "Cellular IPv4", "value": "modem_0001:ipv4"},
        {"label": "Cellular IPv6", "value": "modem_0001:ipv6"},
        {"label": "custom_wan IPv4", "value": "custom_wan:ipv4"},
        {"label": "custom_wan IPv6", "value": "custom_wan:ipv6"},
    ]


async def test_process_user_input_persists_verify_ssl_choice(monkeypatch) -> None:
    def fake_init(self, host: str, hass: Any, verify_ssl: bool = True) -> None:
        self.host = host
        self.username = DEFAULT_USERNAME
        self.router_mac = "00:00:00:00:00:00"
        self.router_model = "mr200"
        self.wan_interfaces = ["wan"]

    async def fake_check_reachable(self) -> bool:
        return True

    async def fake_attempt_login(self, password: str) -> bool:
        return True

    monkeypatch.setattr(SetupHub, "__init__", fake_init)
    monkeypatch.setattr(SetupHub, "check_reachable", fake_check_reachable)
    monkeypatch.setattr(SetupHub, "attempt_login", fake_attempt_login)

    result = await process_user_input(
        {
            "host": "http://router",
            "password": "secret",
            "verify_ssl": False,
        },
        types.SimpleNamespace(),
    )

    assert result["data"]["verify_ssl"] is False


async def test_process_user_input_defaults_verify_ssl_to_false(monkeypatch) -> None:
    def fake_init(self, host: str, hass: Any, verify_ssl: bool = True) -> None:
        self.host = host
        self.username = DEFAULT_USERNAME
        self.router_mac = "00:00:00:00:00:00"
        self.router_model = "mr200"
        self.wan_interfaces = ["wan"]

    async def fake_check_reachable(self) -> bool:
        return True

    async def fake_attempt_login(self, password: str) -> bool:
        return True

    monkeypatch.setattr(SetupHub, "__init__", fake_init)
    monkeypatch.setattr(SetupHub, "check_reachable", fake_check_reachable)
    monkeypatch.setattr(SetupHub, "attempt_login", fake_attempt_login)

    result = await process_user_input(
        {"host": "http://router", "password": "secret"},
        types.SimpleNamespace(),
    )

    assert result["data"]["verify_ssl"] is False


def test_parallel_requests_default_is_false() -> None:
    assert DEFAULT_PARALLEL_REQUESTS is False


async def test_process_user_input_stores_parallel_requests(monkeypatch) -> None:

    def fake_init(self, host: str, hass: Any) -> None:
        self.host = host
        self.username = DEFAULT_USERNAME
        self.router_mac = "00:00:00:00:00:00"
        self.router_model = "mr200"
        self.wan_interfaces = ["wan"]

    async def fake_check_reachable(self) -> bool:
        return True

    async def fake_attempt_login(self, password: str) -> bool:
        return True

    monkeypatch.setattr(SetupHub, "__init__", fake_init)
    monkeypatch.setattr(SetupHub, "check_reachable", fake_check_reachable)
    monkeypatch.setattr(SetupHub, "attempt_login", fake_attempt_login)

    result = await process_user_input(
        {
            "host": "http://router",
            "password": "secret",
            CONF_PARALLEL_REQUESTS: True,
        },
        types.SimpleNamespace(),
    )

    assert result["data"][CONF_PARALLEL_REQUESTS] is True


async def test_process_user_input_defaults_parallel_requests(monkeypatch) -> None:

    def fake_init(self, host: str, hass: Any) -> None:
        self.host = host
        self.username = DEFAULT_USERNAME
        self.router_mac = "00:00:00:00:00:00"
        self.router_model = "mr200"
        self.wan_interfaces = ["wan"]

    async def fake_check_reachable(self) -> bool:
        return True

    async def fake_attempt_login(self, password: str) -> bool:
        return True

    monkeypatch.setattr(SetupHub, "__init__", fake_init)
    monkeypatch.setattr(SetupHub, "check_reachable", fake_check_reachable)
    monkeypatch.setattr(SetupHub, "attempt_login", fake_attempt_login)

    result = await process_user_input(
        {"host": "http://router", "password": "secret"},
        types.SimpleNamespace(),
    )

    assert result["data"][CONF_PARALLEL_REQUESTS] is DEFAULT_PARALLEL_REQUESTS
