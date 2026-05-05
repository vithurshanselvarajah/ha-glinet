def compute_mac_offset(mac: str, delta: int, sep: str = ":") -> str:
    hex_str = mac.replace(sep, "").replace("-", "").lower()
    value = int(hex_str, 16)
    value = (value + delta) & ((1 << 48) - 1)
    new_hex = f"{value:012x}"
    return sep.join(new_hex[index : index + 2] for index in range(0, 12, 2)).lower()
