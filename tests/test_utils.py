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
        (1, "2_4ghz"),
        (6, "2_4ghz"),
        (11, "2_4ghz"),
        (14, "2_4ghz"),
        (36, "5ghz"),
        (44, "5ghz"),
        (149, "5ghz"),
        (165, "5ghz"),
        (177, "5ghz"),
        (None, None),
        (0, None),
        (15, None),
        (35, None),
    ],
)
def test_channel_to_band(channel: int | None, expected: str | None) -> None:
    assert channel_to_band(channel) == expected
