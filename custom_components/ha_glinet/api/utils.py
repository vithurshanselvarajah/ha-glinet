from __future__ import annotations
import re

def decode_firmware_version(version: str) -> tuple[int, int, int, int]:
    """Decode firmware version string into a tuple of 4 integers."""
    numbers = [int(value) for value in re.findall(r"\d+", version)]
    normalized = [*numbers, 0, 0, 0, 0][:4]
    return tuple(normalized)
