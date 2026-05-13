from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TailscaleConnection(Enum):

    DISCONNECTED = 0
    LOGIN_REQUIRED = 1
    AUTHORIZATION_REQUIRED = 2
    CONNECTED = 3
    CONNECTING = 4

@dataclass
class SystemInfo:
    model: str = ""
    firmware_version: str = ""
    mac: str = ""
    sn: str = ""
    device_id: str = ""

@dataclass
class RouterStatus:
    uptime: int = 0
    load_average: list[float] = field(default_factory=list)
    memory_total: int = 0
    memory_free: int = 0
    memory_shared: int = 0
    memory_buffered: int = 0
    temperature: int | None = None
    flash_total: int = 0
    flash_free: int = 0
    network: list[dict[str, Any]] = field(default_factory=list)

@dataclass
class WifiInterfaceInfo:
    enabled: bool = False
    ssid: str = ""
    guest: bool = False
    hidden: bool = False
    encryption: str = ""

@dataclass
class ModemInfo:
    bus: str = ""
    model: str = ""
    imei: str = ""
    iccid: str = ""
    status: str = ""
    signal: int | None = None
    network_type: str = ""
    apn: str = ""
