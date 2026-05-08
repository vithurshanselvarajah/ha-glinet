from __future__ import annotations

import sys
import types
from dataclasses import dataclass


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

from custom_components.ha_glinet.utils import get_first_int, get_first_value  # noqa: E402


def test_first_int_searches_nested_payloads() -> None:
    payload = {"wan": {"status": {"traffic": {"bytes_rx": 1234}}}}

    assert get_first_int(payload, ("bytes_rx",)) == 1234


def test_first_value_searches_nested_payloads() -> None:
    payload = {"modem": {"details": {"operator_name": "Example Mobile"}}}

    assert get_first_value(payload, ("operator_name",)) == "Example Mobile"
