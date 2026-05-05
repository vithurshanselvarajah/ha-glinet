from __future__ import annotations

from datetime import timedelta

from custom_components.ha_glinet.models import ClientDeviceInfo, DeviceInterfaceType


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
