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
        TOTAL="total",
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


def test_sms_sensor_counts_only_unread_messages() -> None:
    from custom_components.ha_glinet.entities.sensor import HUB_SENSORS
    from custom_components.ha_glinet.models import SmsMessage

    desc = next(d for d in HUB_SENSORS if d.key == "sms_messages")

    unread = SmsMessage(message_id="1", phone_number="+44123", text="a", status=0)
    read = SmsMessage(message_id="2", phone_number="+44456", text="b", status=1)
    sent = SmsMessage(message_id="3", phone_number="+44789", text="c", status=2)

    hub = types.SimpleNamespace(
        sms_messages={"1": unread, "2": read, "3": sent},
    )

    assert desc.value_fn(hub) == 1
    attrs = desc.extra_attributes_fn(hub)
    assert attrs["unread_count"] == 1
    assert attrs["message_count"] == 3
    assert attrs["incoming_count"] == 2
    assert attrs["outgoing_count"] == 1


def test_sms_sensor_returns_zero_when_no_unread() -> None:
    from custom_components.ha_glinet.entities.sensor import HUB_SENSORS
    from custom_components.ha_glinet.models import SmsMessage

    desc = next(d for d in HUB_SENSORS if d.key == "sms_messages")

    read = SmsMessage(message_id="1", phone_number="+44123", text="a", status=1)
    sent = SmsMessage(message_id="2", phone_number="+44456", text="b", status=2)

    hub = types.SimpleNamespace(
        sms_messages={"1": read, "2": sent},
    )

    assert desc.value_fn(hub) == 0
    assert desc.extra_attributes_fn(hub)["unread_count"] == 0


def test_cellular_ip_sensors_are_enabled() -> None:
    from custom_components.ha_glinet.entities.sensor import HUB_SENSORS, _sensor_is_enabled

    desc_v4 = next(d for d in HUB_SENSORS if d.key == "cellular_ipv4")
    desc_v6 = next(d for d in HUB_SENSORS if d.key == "cellular_ipv6")

    # Case 1: wan_status_monitors is None (default), modem_0001 is in _wan_interfaces
    hub = types.SimpleNamespace(
        wan_status_monitors=None,
        kmwan_status={
            "interfaces": [
                {"interface": "wan"},
                {"interface": "modem_0001"},
            ]
        }
    )
    assert _sensor_is_enabled(hub, desc_v4) is True
    assert _sensor_is_enabled(hub, desc_v6) is True

    # Case 2: wan_status_monitors is None (default), modem_0001 is NOT in _wan_interfaces
    hub = types.SimpleNamespace(
        wan_status_monitors=None,
        kmwan_status={
            "interfaces": [
                {"interface": "wan"},
                {"interface": "wwan"},
            ]
        }
    )
    assert _sensor_is_enabled(hub, desc_v4) is False
    assert _sensor_is_enabled(hub, desc_v6) is False

    # Case 3: wan_status_monitors is configured, and modem_0001:ipv4 is selected
    hub = types.SimpleNamespace(
        wan_status_monitors={"modem_0001:ipv4", "wan:ipv4"},
        kmwan_status={}
    )
    assert _sensor_is_enabled(hub, desc_v4) is True
    assert _sensor_is_enabled(hub, desc_v6) is False

    # Case 4: wan_status_monitors is configured, and modem_0001:ipv6 is selected
    hub = types.SimpleNamespace(
        wan_status_monitors={"modem_0001:ipv6", "wwan:ipv4"},
        kmwan_status={}
    )
    assert _sensor_is_enabled(hub, desc_v4) is False
    assert _sensor_is_enabled(hub, desc_v6) is True


def test_get_cellular_ip_resolves_correctly() -> None:
    from custom_components.ha_glinet.entities.sensor import _get_cellular_ip

    # Case 1: IPv4 is available, IPv6 is not available
    hub = types.SimpleNamespace(
        cellular_status={
            "modems": [
                {
                    "bus": "0001:01:00.0",
                    "network": {
                        "status": 0,
                        "ipv4": {
                            "gateway": "10.164.158.132",
                            "ip": "10.164.158.131",
                        },
                    },
                }
            ]
        }
    )

    assert _get_cellular_ip(hub, "ipv4") == "10.164.158.131"
    assert _get_cellular_ip(hub, "ipv6") is None

    # Case 2: Both IPv4 and IPv6 are available
    hub = types.SimpleNamespace(
        cellular_status={
            "modems": [
                {
                    "bus": "0001:01:00.0",
                    "network": {
                        "status": 0,
                        "ipv4": {
                            "ip": "10.164.158.131",
                        },
                        "ipv6": {
                            "ip": "2001:db8::1",
                        },
                    },
                }
            ]
        }
    )

    assert _get_cellular_ip(hub, "ipv4") == "10.164.158.131"
    assert _get_cellular_ip(hub, "ipv6") == "2001:db8::1"


