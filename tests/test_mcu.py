from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from custom_components.glinet_router.api.client import GLinetApiClient
from custom_components.glinet_router.api.models import RouterStatus
from custom_components.glinet_router.entities.binary_sensor import GLinetBatteryAbnormalBinarySensor
from custom_components.glinet_router.entities.sensor import HUB_SENSORS
from custom_components.glinet_router.hub import GLinetHub
from tests.test_api_client import FakeSession


async def test_mcu_module_methods_use_expected_payloads() -> None:
    session = FakeSession(
        [
            {"result": {"capacity": {"enable": False, "value": "10"}}},
            {"result": {"err_code": 0, "err_msg": "OK"}},
            {"result": {"screen_display": {"main": True}}},
            {"result": {}},
        ]
    )
    client = GLinetApiClient("http://router/rpc", session, sid="sid-1")

    assert await client.mcu.get_battery_config() == {"capacity": {"enable": False, "value": "10"}}
    assert await client.mcu.set_battery_config({"capacity": {"enable": True, "value": 12}}) == {
        "err_code": 0,
        "err_msg": "OK",
    }
    assert await client.mcu.get_oled_config() == {"screen_display": {"main": True}}
    assert await client.mcu.set_oled_config({"screen_display": {"main": False}}) == {}

    assert [request["json"]["params"] for request in session.requests] == [
        ["sid-1", "mcu", "get_battery_config", {}],
        ["sid-1", "mcu", "set_battery_config", {"capacity": {"enable": True, "value": 12}}],
        ["sid-1", "mcu", "get_config", {}],
        ["sid-1", "mcu", "set_config", {"screen_display": {"main": False}}],
    ]


async def test_hub_mcu_actions_call_api_and_cache_config() -> None:
    hub = GLinetHub.__new__(GLinetHub)
    api_calls: list[tuple[str, Any]] = []

    class McuModule:
        async def get_battery_config(self) -> dict[str, Any]:
            return {"capacity": {"enable": True, "value": 20}}

        async def set_battery_config(self, config: dict[str, Any]) -> None:
            api_calls.append(("set_battery_config", config))

        async def get_oled_config(self) -> dict[str, Any]:
            return {"screen_display": {"main": True, "lan": False}}

        async def set_oled_config(self, config: dict[str, Any]) -> None:
            api_calls.append(("set_oled_config", config))

    async def invoke_api(api_callable: Any) -> Any:
        return await api_callable()

    async def invoke_optional_api(api_callable: Any) -> Any:
        return await api_callable()

    hub._api = SimpleNamespace(mcu=McuModule())
    hub._invoke_api = invoke_api
    hub._invoke_optional_api = invoke_optional_api

    assert await hub.get_mcu_battery_config() == {"capacity": {"enable": True, "value": 20}}
    await hub.set_mcu_battery_config({"capacity": {"enable": False, "value": 10}})
    assert await hub.get_mcu_oled_config() == {"screen_display": {"main": True, "lan": False}}
    await hub.set_mcu_oled_config({"lan": True})

    assert api_calls == [
        ("set_battery_config", {"capacity": {"enable": False, "value": 10}}),
        ("set_oled_config", {"screen_display": {"main": True, "lan": True}}),
    ]


async def test_fetch_system_status_preserves_mcu_battery_status() -> None:
    session = FakeSession(
        [
            {
                "result": {
                    "uptime": 1,
                    "mcu": {
                        "temperature": 37,
                        "charging_status": 1,
                        "charge_percent": 96,
                        "abnormal": False,
                    },
                }
            }
        ]
    )
    client = GLinetApiClient("http://router/rpc", session, sid="sid-1")

    status = await client.system.get_status()

    assert status.mcu == {
        "temperature": 37,
        "charging_status": 1,
        "charge_percent": 96,
        "abnormal": False,
    }


def test_battery_sensors_read_mcu_status_when_enabled() -> None:
    hub = SimpleNamespace(
        router_status=RouterStatus(
            mcu={
                "temperature": 37,
                "charging_status": 1,
                "charge_percent": 96,
                "charge_cnt": 19,
                "fastcharge": 0,
                "abnormal_type": 0,
            }
        )
    )
    sensors = {description.key: description for description in HUB_SENSORS}

    assert sensors["battery_temperature"].value_fn(hub) == 37
    assert sensors["battery_charge"].value_fn(hub) == 96
    assert sensors["battery_charging_status"].value_fn(hub) == "charging"
    assert sensors["battery_charge"].extra_attributes_fn(hub) == {
        "charge_count": 19,
        "fast_charge": 0,
        "abnormal_type": 0,
    }


def test_battery_abnormal_binary_sensor_reads_mcu_status() -> None:
    hub = SimpleNamespace(
        router_status=RouterStatus(mcu={"abnormal": True, "abnormal_type": 2}),
        device_mac="00:11:22:33:44:55",
        device_info={},
    )

    sensor = GLinetBatteryAbnormalBinarySensor(hub)

    assert sensor.unique_id == "glinet_binary_sensor/00:11:22:33:44:55/battery_abnormal"
    assert sensor.is_on is True
    assert sensor.extra_state_attributes == {"abnormal_type": 2}
