import pytest

from custom_components.ha_glinet.utils import channel_to_band, compute_mac_offset


@pytest.mark.parametrize(
    ("mac", "delta", "expected"),
    [
        ("00:00:00:00:00:01", 1, "00:00:00:00:00:02"),
        ("00-00-00-00-00-01", 1, "00:00:00:00:00:02"),
        ("00:00:00:00:00:10", -1, "00:00:00:00:00:0f"),
        ("ff:ff:ff:ff:ff:ff", 1, "00:00:00:00:00:00"),
        ("00:00:00:00:00:00", -1, "ff:ff:ff:ff:ff:ff"),
    ],
)
def test_compute_mac_offset(mac: str, delta: int, expected: str) -> None:
    assert compute_mac_offset(mac, delta) == expected


def test_compute_mac_offset_supports_custom_separator() -> None:
    assert compute_mac_offset("00-00-00-00-00-01", 1, sep="-") == "00-00-00-00-00-02"


@pytest.mark.parametrize(
    ("channel", "expected"),
    [
        (1, "2.4GHz"),
        (6, "2.4GHz"),
        (11, "2.4GHz"),
        (14, "2.4GHz"),
        (36, "5GHz"),
        (44, "5GHz"),
        (149, "5GHz"),
        (165, "5GHz"),
        (177, "5GHz"),
        (None, None),
        (0, None),
        (15, None),
        (35, None),
    ],
)
def test_channel_to_band(channel: int | None, expected: str | None) -> None:
    assert channel_to_band(channel) == expected
