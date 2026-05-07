from datetime import datetime
from typing import Any


def compute_mac_offset(mac: str, delta: int, sep: str = ":") -> str:
    hex_str = mac.replace(sep, "").replace("-", "").lower()
    value = int(hex_str, 16)
    value = (value + delta) & ((1 << 48) - 1)
    new_hex = f"{value:012x}"
    return sep.join(new_hex[index : index + 2] for index in range(0, 12, 2)).lower()


def get_first_int(data: Any, keys: tuple[str, ...], nested: tuple[str, ...] = ()) -> int | None:
    for source in _candidate_dicts(data, nested):
        for key in keys:
            value = source.get(key)
            if isinstance(value, bool):
                continue
            if isinstance(value, int):
                return value
            if isinstance(value, float):
                return int(value)
    return None


def get_first_value(data: Any, keys: tuple[str, ...], nested: tuple[str, ...] = ()) -> str | None:
    for source in _candidate_dicts(data, nested):
        for key in keys:
            value = source.get(key)
            if value not in (None, ""):
                return str(value)
    return None


def get_first_bool(data: dict[str, Any], keys: tuple[str, ...]) -> bool | None:
    for key in keys:
        value = data.get(key)
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            return value != 0
        if isinstance(value, str):
            lowered = value.lower()
            if lowered in {"1", "true", "on", "enabled", "enable"}:
                return True
            if lowered in {"0", "false", "off", "disabled", "disable"}:
                return False
    return None


def calculate_rate(
    prev_val: int | None,
    curr_val: int | None,
    prev_time: datetime | None,
    curr_time: datetime,
) -> int | None:
    if prev_val is None or curr_val is None or prev_time is None:
        return None
    elapsed = (curr_time - prev_time).total_seconds()
    if elapsed <= 0 or curr_val < prev_val:
        return None
    return int((curr_val - prev_val) / elapsed)


def _candidate_dicts(data: Any, nested: tuple[str, ...]) -> list[dict[str, Any]]:
    if not isinstance(data, dict):
        return []
    candidates = [data]
    for key in nested:
        value = data.get(key)
        if isinstance(value, dict):
            candidates.append(value)
    candidates.extend(_walk_nested_dicts(data))
    return candidates


def _walk_nested_dicts(value: Any) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    if isinstance(value, dict):
        for child in value.values():
            if isinstance(child, dict):
                candidates.append(child)
                candidates.extend(_walk_nested_dicts(child))
            elif isinstance(child, list):
                candidates.extend(_walk_nested_dicts(child))
    elif isinstance(value, list):
        for child in value:
            candidates.extend(_walk_nested_dicts(child))
    return candidates
