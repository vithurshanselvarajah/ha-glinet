from __future__ import annotations

import sys
import types
from dataclasses import dataclass

from custom_components.ha_glinet.utils import get_first_int, get_first_value


def _install_sensor_dependency_stubs() -> None:
    @dataclass(frozen=True, kw_only=True)
    class SensorEntityDescription:
        key: str
        name: str | None = None
        has_entity_name: bool | None = None
        icon: str | None = None
        entity_category: str | None = None
        device_class: str | None = None
        native_unit_of_measurement: str | None = None
        state_class: str | None = None
        suggested_display_precision: int | None = None
        options: list[str] | None = None

    sensor = types.ModuleType("homeassistant.components.sensor")
    sensor.SensorDeviceClass = types.SimpleNamespace(
        DATA_RATE="data_rate",
        DATA_SIZE="data_size",
        ENUM="enum",
        TEMPERATURE="temperature",
        TIMESTAMP="timestamp",
    )
    sensor.SensorEntity = object
    sensor.SensorEntityDescription = SensorEntityDescription
    sensor.SensorStateClass = types.SimpleNamespace(
        MEASUREMENT="measurement",
        TOTAL_INCREASING="total_increasing",
    )
    sys.modules.setdefault("homeassistant.components.sensor", sensor)

    const = sys.modules["homeassistant.const"]
    const.PERCENTAGE = "%"
    const.EntityCategory = types.SimpleNamespace(DIAGNOSTIC="diagnostic")
    const.UnitOfTemperature = types.SimpleNamespace(CELSIUS="C")

    core = types.ModuleType("homeassistant.core")
    core.HomeAssistant = object
    core.callback = lambda func: func
    sys.modules.setdefault("homeassistant.core", core)

    entity_platform = types.ModuleType("homeassistant.helpers.entity_platform")
    entity_platform.AddEntitiesCallback = object
    sys.modules.setdefault("homeassistant.helpers.entity_platform", entity_platform)


_install_sensor_dependency_stubs()


def test_first_int_searches_nested_payloads() -> None:
    payload = {"wan": {"status": {"traffic": {"bytes_rx": 1234}}}}

    assert get_first_int(payload, ("bytes_rx",)) == 1234


def test_first_value_searches_nested_payloads() -> None:
    payload = {"modem": {"details": {"operator_name": "Example Mobile"}}}

    assert get_first_value(payload, ("operator_name",)) == "Example Mobile"


def test_wan_status_helpers_report_interface_protocol_state() -> None:
    from custom_components.ha_glinet.entities.sensor import (
        WanStatusSensor,
        _wan_interface_by_name,
        _wan_protocol_status,
    )

    hub = types.SimpleNamespace(
        kmwan_status={
            "interfaces": [
                {"interface": "wan", "status_v4": 0, "status_v6": 1},
                {"interface": "wwan", "status_v4": 1, "status_v6": 0},
            ]
        }
    )

    wan = _wan_interface_by_name(hub, "wan")
    assert _wan_protocol_status(wan, "ipv4") == "Up"
    assert _wan_protocol_status(wan, "ipv6") == "Down"

    wwan = _wan_interface_by_name(hub, "wwan")
    assert _wan_protocol_status(wwan, "ipv4") == "Down"
    assert _wan_protocol_status(wwan, "ipv6") == "Up"

    assert _wan_protocol_status(None, "ipv4") == "Unknown"

    hub.device_mac = "00:11:22:33:44:55"
    hub.device_info = {}
    hub.hass = object()
    sensor = WanStatusSensor(hub, "wan", {"ipv4", "ipv6"})

    assert sensor._attr_name == "Ethernet 1 status"
    assert sensor.unique_id == "glinet_sensor/00:11:22:33:44:55/wan_status_wan"
    assert sensor.native_value == "Up"
    assert sensor.extra_state_attributes == {
        "interface": "wan",
        "interface_name": "Ethernet 1",
        "monitored_protocols": ["ipv4", "ipv6"],
        "ipv4_status": "Up",
        "ipv6_status": "Down",
        "status_v4": 0,
        "status_v6": 1,
    }

    sensor = WanStatusSensor(hub, "wan", {"ipv6"})
    assert sensor.native_value == "Down"

    unknown_sensor = WanStatusSensor(hub, "custom_wan", {"ipv4"})
    assert unknown_sensor._attr_name == "custom_wan status"
