from __future__ import annotations

from datetime import timedelta

from custom_components.ha_glinet.models import (
    ClientDeviceInfo,
    DeviceInterfaceType,
    FanStatus,
    SmsDirection,
    SmsMessage,
    SmsStatus,
)


def test_client_device_uses_alias_before_name() -> None:
    device = ClientDeviceInfo("aa:bb:cc:dd:ee:ff")

    device.apply_update(
        {
            "alias": "Preferred name",
            "name": "Fallback name",
            "ip": "192.168.8.20",
            "online": True,
            "type": 1,
        }
    )

    assert device.name == "Preferred name"
    assert device.ip_address == "192.168.8.20"
    assert device.is_connected is True
    assert device.interface_type == DeviceInterfaceType.WIFI_5


def test_client_device_falls_back_to_mac_when_name_is_missing() -> None:
    device = ClientDeviceInfo("aa:bb:cc:dd:ee:ff")

    device.apply_update({"alias": "", "name": "*", "online": True, "type": 999})

    assert device.name == "aa_bb_cc_dd_ee_ff"
    assert device.interface_type == DeviceInterfaceType.UNKNOWN


def test_client_device_extracts_bandwidth_from_common_keys() -> None:
    device = ClientDeviceInfo("aa:bb:cc:dd:ee:ff")

    device.apply_update(
        {
            "online": True,
            "rx_bytes": 1000,
            "tx": 2000,
            "download_speed": 300,
            "up_speed": 400,
        }
    )

    assert device.rx_bytes == 1000
    assert device.tx_bytes == 2000
    assert device.rx_rate == 300
    assert device.tx_rate == 400


def test_sms_message_direction_incoming() -> None:
    msg = SmsMessage(message_id="1", phone_number="123", text="hi", status=SmsStatus.UNREAD)
    assert msg.direction == SmsDirection.INCOMING

    msg.status = SmsStatus.READ
    assert msg.direction == SmsDirection.INCOMING


def test_sms_message_direction_outgoing() -> None:
    msg = SmsMessage(message_id="1", phone_number="123", text="hi", status=SmsStatus.SENT)
    assert msg.direction == SmsDirection.OUTGOING

    msg.status = SmsStatus.SENDING
    assert msg.direction == SmsDirection.OUTGOING

    msg.status = SmsStatus.WAITING
    assert msg.direction == SmsDirection.OUTGOING

    msg.status = SmsStatus.FAILED
    assert msg.direction == SmsDirection.OUTGOING


def test_sms_message_direction_unknown() -> None:
    msg = SmsMessage(message_id="1", phone_number="123", text="hi", status=None)
    assert msg.direction == SmsDirection.UNKNOWN

    msg.status = 999  # Unknown status
    assert msg.direction == SmsDirection.UNKNOWN


def test_sms_message_status_label() -> None:
    msg = SmsMessage(message_id="1", phone_number="123", text="hi", status=SmsStatus.UNREAD)
    assert msg.status_label == "Unread"

    msg.status = SmsStatus.SENT
    assert msg.status_label == "Sent"

    msg.status = SmsStatus.FAILED
    assert msg.status_label == "Failed"

    msg.status = None
    assert msg.status_label == "Unknown"

    msg.status = 999
    assert msg.status_label == "Unknown (999)"


def test_client_device_computes_rates_from_byte_deltas() -> None:
    device = ClientDeviceInfo("aa:bb:cc:dd:ee:ff")
    device.apply_update({"online": True, "rx_bytes": 1000, "tx_bytes": 2000})
    device._last_traffic_update = device._last_traffic_update - timedelta(seconds=10)

    device.apply_update({"online": True, "rx_bytes": 1300, "tx_bytes": 2600})

    assert device.rx_rate == 30
    assert device.tx_rate == 60


def test_client_device_consider_home_keeps_recent_device_connected() -> None:
    device = ClientDeviceInfo("aa:bb:cc:dd:ee:ff")
    device.apply_update({"online": True})

    device.apply_update(None, consider_home=900)

    assert device.is_connected is True
    assert device.ip_address is None


def test_client_device_marks_missing_device_away_when_delay_is_zero() -> None:
    device = ClientDeviceInfo("aa:bb:cc:dd:ee:ff")
    device.apply_update({"online": True})

    device.apply_update(None, consider_home=0)

    assert device.is_connected is False


def test_fan_status_from_api_response() -> None:
    status = {"status": True, "speed": 1000}
    config = {"temperature": 75, "warn_temperature": 90}
    fan = FanStatus.from_api_response(status, config)
    assert fan.running is True
    assert fan.speed == 1000
    assert fan.temperature_threshold == 75
    assert fan.warn_temperature == 90
