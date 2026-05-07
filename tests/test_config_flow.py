from __future__ import annotations

import types
from typing import Any

from custom_components.ha_glinet.config_flow import (
    CONF_ENABLED_FEATURES,
    DEFAULT_ENABLED_FEATURES,
    SetupHub,
    process_user_input,
)
from custom_components.ha_glinet.const import DEFAULT_USERNAME, FEATURE_REPEATER, FEATURE_WIREGUARD


async def test_process_user_input_stores_enabled_features(monkeypatch) -> None:
    def fake_init(self, host: str, hass: Any) -> None:
        self.host = host
        self.username = DEFAULT_USERNAME
        self.router_mac = "00:00:00:00:00:00"
        self.router_model = "mr200"

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


async def test_process_user_input_defaults_enabled_features_when_missing(monkeypatch) -> None:
    def fake_init(self, host: str, hass: Any) -> None:
        self.host = host
        self.username = DEFAULT_USERNAME
        self.router_mac = "00:00:00:00:00:00"
        self.router_model = "mr200"

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
    assert FEATURE_WIREGUARD in result["data"][CONF_ENABLED_FEATURES]
