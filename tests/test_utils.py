import pytest

from custom_components.ha_glinet.utils import compute_mac_offset


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
