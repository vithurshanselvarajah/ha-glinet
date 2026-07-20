from __future__ import annotations

from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, MagicMock

from custom_components.glinet_router.api.client import GLinetApiClient
from custom_components.glinet_router.const import (
    CONF_ENABLED_FEATURES,
    FEATURE_PARENTAL_CONTROL,
)
from custom_components.glinet_router.entities.select import GLinetClientParentalGroupSelect
from custom_components.glinet_router.entities.switch import GLinetClientInternetAccessSwitch
from custom_components.glinet_router.hub import GLinetHub
from custom_components.glinet_router.models import ClientDeviceInfo, ParentalGroup, ParentalStatus
from tests.test_api_client import FakeSession


async def test_parental_and_access_modules_use_expected_payloads() -> None:
    session = FakeSession(
        [
            {"result": {"enable": True}},
            {"result": {"ok": True}},
            {"result": {"groups": []}},
            {"result": {"brief": False}},
            {"result": {"ok": True}},
            {"result": {"ok": True}},
            {"result": {"mode": 1}},
            {"result": {"ok": True}},
            {"result": {"ok": True}},
            {"result": {"mode": "black", "black_mac": []}},
            {"result": {"ok": True}},
            {"result": {"ok": True}},
        ]
    )
    client = GLinetApiClient("http://router/rpc", session, sid="sid-1")

    await client.parental_control.get_config()
    await client.parental_control.set_config(True)
    await client.parental_control.get_status()
    await client.parental_control.get_brief("group1")
    await client.parental_control.set_brief(True, "01:00:00", "drop", "group1", False)
    await client.parental_control.set_group("group1", name="Kids")
    await client.parental_control.get_mode()
    await client.parental_control.set_mode(1)
    await client.parental_control.update()
    await client.black_white_list.get_config()
    await client.black_white_list.set_config("black", ["aa:bb"])
    await client.black_white_list.set_single_mac("black", "add", "aa:bb")

    assert [request["json"]["params"] for request in session.requests] == [
        ["sid-1", "parental-control", "get_config", {}],
        ["sid-1", "parental-control", "set_config", {"enable": True}],
        ["sid-1", "parental-control", "get_status", {}],
        ["sid-1", "parental-control", "get_brief", {"group_id": "group1"}],
        [
            "sid-1",
            "parental-control",
            "set_brief",
            {
                "enable": True,
                "time": "01:00:00",
                "rule_id": "drop",
                "group_id": "group1",
                "manual_stop": False,
            },
        ],
        ["sid-1", "parental-control", "set_group", {"id": "group1", "name": "Kids"}],
        ["sid-1", "parental-control", "get_mode", {}],
        ["sid-1", "parental-control", "set_mode", {"mode": 1}],
        ["sid-1", "parental-control", "update", {}],
        ["sid-1", "black_white_list", "get_config", {}],
        ["sid-1", "black_white_list", "set_config", {"mode": "black", "mac": ["aa:bb"]}],
        [
            "sid-1",
            "black_white_list",
            "set_single_mac",
            {"mode": "black", "operate": "add", "mac": "aa:bb"},
        ],
    ]


async def test_parental_status_merges_config_and_status_groups() -> None:
    status = ParentalStatus.from_api_response(
        {
            "enable": True,
            "groups": [{"id": "group1", "name": "Kids", "mac": ["AA:BB"]}],
        },
        {"groups": [{"id": "group1", "rule": "drop", "brief": True}]},
        {"mode": 1},
    )

    group = status.groups["group1"]
    assert status.enabled is True
    assert status.mode == 1
    assert group.name == "Kids"
    assert group.macs == ["aa:bb"]
    assert group.rule == "drop"
    assert group.brief is True


async def test_hub_fetches_parental_and_access_state() -> None:
    hub = GLinetHub.__new__(GLinetHub)
    hub._api = SimpleNamespace(
        parental_control=SimpleNamespace(
            get_config=object(),
            get_status=object(),
            get_mode=object(),
        ),
        black_white_list=SimpleNamespace(get_config=object()),
    )
    hub._invoke_optional_api = AsyncMock(
        side_effect=[
            {"enable": True, "groups": [{"id": "group1", "name": "Kids"}]},
            {"groups": [{"id": "group1", "brief": True}]},
            {"mode": 1},
            {"mode": "black", "black_mac": ["aa:bb:cc:dd:ee:ff"]},
        ]
    )

    await hub.fetch_parental_control_status()
    await hub.fetch_access_control_config()

    assert hub.parental_control_enabled is True
    assert hub.parental_groups["group1"].brief is True
    assert hub.access_control_mode == "black"
    assert hub.device_internet_access_enabled("aa:bb:cc:dd:ee:ff") is False


async def test_hub_parental_mutations_call_api_and_refresh() -> None:
    hub = GLinetHub.__new__(GLinetHub)
    hub._parental_status = ParentalStatus(
        groups={
            "group1": ParentalGroup(
                id="group1",
                name="Kids",
                macs=["aa:bb"],
                raw={"id": "group1", "name": "Kids", "mac": ["aa:bb"]},
            )
        }
    )
    hub._access_control_mode = "black"
    calls: list[tuple[str, Any]] = []

    class ParentalModule:
        async def set_config(self, enabled: bool) -> None:
            calls.append(("set_config", enabled))

        async def set_group(self, group_id: str, **params: Any) -> None:
            calls.append(("set_group", group_id, params))

        async def set_brief(
            self,
            enable: bool,
            time: str,
            rule_id: str,
            group_id: str,
            manual_stop: bool,
        ) -> None:
            calls.append(("set_brief", enable, time, rule_id, group_id, manual_stop))

        async def set_mode(self, mode: int) -> None:
            calls.append(("set_mode", mode))

        async def update(self) -> None:
            calls.append(("update", None))

    class AccessModule:
        async def set_single_mac(self, mode: str, operate: str, mac: str) -> None:
            calls.append(("set_single_mac", mode, operate, mac))

    async def invoke_api(api_callable: Any) -> Any:
        return await api_callable()

    async def refresh_parental() -> None:
        calls.append(("refresh_parental", None))

    async def refresh_access() -> None:
        calls.append(("refresh_access", None))

    hub._api = SimpleNamespace(
        parental_control=ParentalModule(),
        black_white_list=AccessModule(),
    )
    hub._invoke_api = invoke_api
    hub.fetch_parental_control_status = refresh_parental
    hub.fetch_access_control_config = refresh_access

    await hub.set_parental_control_enabled(True)
    await hub.set_group_enabled("group1", False)
    await hub.set_temporary_override("group1", True, "", "drop")
    await hub.set_parental_mode(1)
    await hub.update_parental_signatures()
    await hub.set_single_device_block("AA:BB", True)

    assert ("set_config", True) in calls
    assert any(call[0] == "set_group" and call[1] == "group1" for call in calls)
    assert ("set_brief", True, "", "drop", "group1", False) in calls
    assert ("set_mode", 1) in calls
    assert ("update", None) in calls
    assert ("set_single_mac", "black", "add", "aa:bb") in calls


async def test_client_entities_are_associated_with_client_device() -> None:
    hub = SimpleNamespace(
        device_mac="00:11:22:33:44:55",
        device_info={},
        router_id="router",
        hass=object(),
        device_internet_access_enabled=lambda mac: True,
        access_control_mode="black",
        set_single_device_block=AsyncMock(),
        async_request_refresh=AsyncMock(),
        parental_groups={"group1": ParentalGroup("group1", "Kids", macs=["aa:bb"])},
        parental_group_for_device=lambda mac: None,
        assign_device_to_parental_group=AsyncMock(),
    )
    device = ClientDeviceInfo("aa:bb")
    switch = GLinetClientInternetAccessSwitch(hub, device)
    select = GLinetClientParentalGroupSelect(hub, device)

    assert switch.unique_id == "glinet_switch/aa:bb/internet_access"
    assert select.unique_id == "glinet_select/aa:bb/parental_control_group"
    assert ("mac", "aa:bb") in switch._attr_device_info["connections"]
    assert ("mac", "aa:bb") in select._attr_device_info["connections"]


async def test_fetch_all_data_includes_and_resets_parental_control() -> None:
    hub = GLinetHub.__new__(GLinetHub)
    hub._settings = {CONF_ENABLED_FEATURES: [FEATURE_PARENTAL_CONTROL]}
    hub._entry = SimpleNamespace(entry_id="entry")
    hub._host = "192.168.8.1"
    hub.hass = object()
    called: list[str] = []

    async def record(name: str) -> None:
        called.append(name)

    hub.refresh_session_token = AsyncMock()
    hub.fetch_system_status = lambda: record("system")
    hub.fetch_kmwan_status = lambda: record("kmwan")
    hub.fetch_connected_devices = lambda: record("clients")
    hub.fetch_wifi_interfaces = lambda: record("wifi")
    hub.fetch_fan_status = lambda: record("fan")
    hub.fetch_led_status = lambda: record("led")
    hub.fetch_parental_control_status = lambda: record("parental")
    hub.fetch_access_control_config = lambda: record("access")

    await hub.fetch_all_data()

    assert called == ["system", "kmwan", "clients", "wifi", "fan", "led", "parental", "access"]

    hub._settings = {CONF_ENABLED_FEATURES: []}
    hub._parental_status = ParentalStatus(enabled=True)
    hub._access_control_config = {"mode": "white"}
    hub._black_mac = ["aa:bb"]
    hub._white_mac = ["cc:dd"]
    called.clear()

    await hub.fetch_all_data()

    assert hub.parental_control_enabled is None
    assert hub._access_control_config == {}
    assert hub.black_mac == []
    assert hub.white_mac == []


async def test_async_initialize_hub_cleans_up_parental_control_entities(
    monkeypatch,
) -> None:
    import custom_components.glinet_router.hub as hub_module

    hub = GLinetHub.__new__(GLinetHub)
    hub._settings = {CONF_ENABLED_FEATURES: []}
    hub._entry = SimpleNamespace(entry_id="entry")
    hub.hass = MagicMock()
    hub._late_init_complete = True
    hub._factory_mac = "00:11:22:33:44:55"

    entries = [
        SimpleNamespace(
            entity_id="switch.parental_control",
            unique_id="glinet_switch/00:11:22:33:44:55/parental_control",
            domain="switch",
        ),
        SimpleNamespace(
            entity_id="switch.internet_access",
            unique_id="glinet_switch/aa:bb:cc:dd:ee:ff/internet_access",
            domain="switch",
        ),
        SimpleNamespace(
            entity_id="select.parental_control_group",
            unique_id="glinet_select/aa:bb:cc:dd:ee:ff/parental_control_group",
            domain="select",
        ),
        SimpleNamespace(
            entity_id="binary_sensor.parental_override",
            unique_id=(
                "glinet_binary_sensor/00:11:22:33:44:55/parental_control_group_group1_override"
            ),
            domain="binary_sensor",
        ),
        SimpleNamespace(
            entity_id="sensor.uptime",
            unique_id="glinet_sensor/00:11:22:33:44:55/system_uptime",
            domain="sensor",
        ),
    ]
    entity_registry = MagicMock()

    monkeypatch.setattr(hub_module.er, "async_get", lambda _: entity_registry)
    monkeypatch.setattr(
        hub_module.er,
        "async_entries_for_config_entry",
        lambda *_: entries,
    )
    hub.fetch_all_data = AsyncMock()

    await hub.async_initialize_hub()

    assert entity_registry.async_remove.call_count == 4
    entity_registry.async_remove.assert_any_call("switch.parental_control")
    entity_registry.async_remove.assert_any_call("switch.internet_access")
    entity_registry.async_remove.assert_any_call("select.parental_control_group")
    entity_registry.async_remove.assert_any_call("binary_sensor.parental_override")
