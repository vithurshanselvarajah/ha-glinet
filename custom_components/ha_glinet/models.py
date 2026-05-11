from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import IntEnum, StrEnum

from homeassistant.util import dt as dt_util

from .utils import calculate_rate, get_first_int


class RepeaterState(IntEnum):
    NOT_USED = 0
    CONNECTING = 1
    CONNECTED = 2
    FAILED = 3


@dataclass(slots=True)
class RepeaterStatus:
    state: RepeaterState
    ssid: str | None = None
    bssid: str | None = None
    channel: int | None = None
    signal: int | None = None
    ipv4_address: str | None = None
    ipv4_gateway: str | None = None
    ipv4_dns: list[str] | None = None
    device: str | None = None
    fail_type: str | None = None

    @classmethod
    def from_api_response(cls, data: dict) -> RepeaterStatus:
        ipv4 = data.get("ipv4") or {}
        dns_list = ipv4.get("dns")
        return cls(
            state=RepeaterState(data.get("state", 0)),
            ssid=data.get("ssid"),
            bssid=data.get("bssid"),
            channel=data.get("channel"),
            signal=data.get("signal"),
            ipv4_address=ipv4.get("ip"),
            ipv4_gateway=ipv4.get("gateway"),
            ipv4_dns=dns_list if isinstance(dns_list, list) else None,
            device=data.get("device"),
            fail_type=data.get("fail_type"),
        )


@dataclass(slots=True)
class FanStatus:
    running: bool
    speed: int | None = None
    temperature_threshold: int | None = None
    warn_temperature: int | None = None

    @classmethod
    def from_api_response(cls, status: dict, config: dict) -> FanStatus:
        return cls(
            running=status.get("status", False),
            speed=status.get("speed"),
            temperature_threshold=config.get("temperature"),
            warn_temperature=config.get("warn_temperature"),
        )


@dataclass(slots=True)
class ScannedNetwork:
    ssid: str
    bssid: str
    signal: int
    band: str
    encryption_enabled: bool
    encryption_type: str
    saved: bool
    channel: int | None = None

    @classmethod
    def from_api_response(cls, data: dict) -> ScannedNetwork:
        encryption = data.get("encryption") or {}
        return cls(
            ssid=data.get("ssid", ""),
            bssid=data.get("bssid", ""),
            signal=data.get("signal", 0),
            band=data.get("band", ""),
            encryption_enabled=encryption.get("enabled", False),
            encryption_type=encryption.get("description", "Open"),
            saved=data.get("saved", False),
            channel=data.get("channel"),
        )


class DeviceInterfaceType(StrEnum):
    WIFI_24 = "2.4GHz"
    WIFI_5 = "5GHz"
    LAN = "LAN"
    WIFI_24_GUEST = "2.4GHz Guest"
    WIFI_5_GUEST = "5GHz Guest"
    UNKNOWN = "Unknown"
    DONGLE = "Dongle"
    BYPASS_ROUTE = "Bypass Route"
    UNKNOWN2 = "Unknown"
    MLO = "MLO"
    MLO_GUEST = "MLO Guest"
    WIFI_6 = "6GHz"
    WIFI_6_GUEST = "6GHz Guest"


@dataclass(slots=True)
class WireGuardClient:
    name: str
    connected: bool = field(compare=False)
    group_id: int = 0
    peer_id: int = 0
    tunnel_id: int | None = None


@dataclass(slots=True)
class WireGuardServerStatus:
    enabled: bool
    initialization: bool
    tunnel_ip: str | None = None
    connected_peers: int = 0
    total_peers: int = 0
    rx_bytes: int = 0
    tx_bytes: int = 0

    @classmethod
    def from_api_response(cls, data: dict) -> WireGuardServerStatus:
        server = data.get("server") or {}
        peers = data.get("peers") or []
        connected_count = sum(1 for p in peers if p.get("status") == 1)
        return cls(
            enabled=server.get("status") == 1,
            initialization=server.get("initialization", False),
            tunnel_ip=server.get("tunnel_ip"),
            connected_peers=connected_count,
            total_peers=len(peers),
            rx_bytes=server.get("rx_bytes", 0),
            tx_bytes=server.get("tx_bytes", 0),
        )
    

@dataclass(slots=True)
class OpenVpnClient:
    name: str
    connected: bool = field(compare=False)
    group_id: int = 0
    client_id: int = 0
    group_name: str | None = None
    location: str | None = None
    locations: list[str] = field(default_factory=list)
    remotes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class OpenVpnServerStatus:
    enabled: bool
    initialization: bool
    tunnel_ip: str | None = None
    connected_users: int = 0
    total_users: int = 0
    rx_bytes: int = 0
    tx_bytes: int = 0

    @classmethod
    def from_api_response(cls, data: dict, users: list[dict]) -> OpenVpnServerStatus:
        status = data.get("status")
        return cls(
            enabled=status == 1,
            initialization=data.get("initialization", False),
            tunnel_ip=data.get("tunnel_ip"),
            connected_users=len(users),
            total_users=len(users),
            rx_bytes=data.get("rx_bytes", 0),
            tx_bytes=data.get("tx_bytes", 0),
        )


@dataclass(slots=True)
class ZeroTierStatus:
    enabled: bool
    network_id: str | None
    connected: bool
    zerotier_ip: str | None
    lan_ip: str | None
    wan_ip: str | None

    @classmethod
    def from_api_response(cls, config: dict, status: dict) -> ZeroTierStatus:
        return cls(
            enabled=config.get("enable", False),
            network_id=config.get("id"),
            connected=status.get("status") == 0,
            zerotier_ip=status.get("zerotier_ip"),
            lan_ip=status.get("lan_ip"),
            wan_ip=status.get("wan_ip"),
        )


@dataclass(slots=True)
class WifiInterface:
    name: str
    enabled: bool
    ssid: str
    guest: bool
    hidden: bool
    encryption: str


class SmsDirection(StrEnum):
    INCOMING = "incoming"
    OUTGOING = "outgoing"
    UNKNOWN = "unknown"


class SmsStatus(IntEnum):
    UNREAD = 0
    READ = 1
    SENT = 2
    SENDING = 3
    WAITING = 4
    FAILED = 5


@dataclass(slots=True)
class SmsMessage:
    message_id: str
    phone_number: str
    text: str
    bus: str | None = None
    status: int | None = None
    timestamp: str | None = None
    read: bool | None = None

    @property
    def direction(self) -> SmsDirection:
        if self.status is None:
            return SmsDirection.UNKNOWN
        if self.status in {SmsStatus.UNREAD, SmsStatus.READ}:
            return SmsDirection.INCOMING
        if self.status in {SmsStatus.SENT, SmsStatus.SENDING, SmsStatus.WAITING, SmsStatus.FAILED}:
            return SmsDirection.OUTGOING
        return SmsDirection.UNKNOWN

    @property
    def status_label(self) -> str:
        status_labels = {
            SmsStatus.UNREAD: "Unread",
            SmsStatus.READ: "Read",
            SmsStatus.SENT: "Sent",
            SmsStatus.SENDING: "Sending",
            SmsStatus.WAITING: "Waiting",
            SmsStatus.FAILED: "Failed",
        }
        if self.status is None:
            return "Unknown"
        return status_labels.get(self.status, f"Unknown ({self.status})")


class ClientDeviceInfo:
    def __init__(self, mac: str, name: str | None = None) -> None:
        self._mac = mac
        self._name = name
        self._ip_address: str | None = None
        self._last_activity = dt_util.utcnow() - timedelta(days=1)
        self._connected = False
        self._interface_type = DeviceInterfaceType.UNKNOWN
        self._rx_bytes: int | None = None
        self._tx_bytes: int | None = None
        self._rx_rate: int | None = None
        self._tx_rate: int | None = None
        self._last_traffic_update: datetime | None = None
        self._is_known = True

    def apply_update(self, dev_info: dict | None = None, consider_home: int = 0) -> None:
        now = dt_util.utcnow()
        if dev_info:
            alias = str(dev_info.get("alias", "")).strip()
            name = str(dev_info.get("name", "")).strip()
            if alias:
                self._name = alias
            elif name and name != "*":
                self._name = name
            else:
                self._name = self._mac.replace(":", "_")
            self._ip_address = dev_info.get("ip")
            self._last_activity = now
            self._connected = bool(dev_info.get("online", False))
            type_index = int(dev_info.get("type", 5))
            interface_types = list(DeviceInterfaceType)
            if 0 <= type_index < len(interface_types):
                self._interface_type = interface_types[type_index]
            else:
                self._interface_type = DeviceInterfaceType.UNKNOWN
            previous_rx_bytes = self._rx_bytes
            previous_tx_bytes = self._tx_bytes
            previous_traffic_update = self._last_traffic_update
            self._rx_bytes = get_first_int(
                dev_info,
                ("rx_bytes", "bytes_rx", "rx", "download", "down"),
            )
            self._tx_bytes = get_first_int(
                dev_info,
                ("tx_bytes", "bytes_tx", "tx", "upload", "up"),
            )
            explicit_rx_rate = get_first_int(
                dev_info,
                ("rx_rate", "rx_speed", "rx_bps", "download_speed", "down_speed", "down_rate"),
            )
            explicit_tx_rate = get_first_int(
                dev_info,
                ("tx_rate", "tx_speed", "tx_bps", "upload_speed", "up_speed", "up_rate"),
            )
            self._rx_rate = explicit_rx_rate or calculate_rate(
                previous_rx_bytes,
                self._rx_bytes,
                previous_traffic_update,
                now,
            )
            self._tx_rate = explicit_tx_rate or calculate_rate(
                previous_tx_bytes,
                self._tx_bytes,
                previous_traffic_update,
                now,
            )
            if self._rx_bytes is not None or self._tx_bytes is not None:
                self._last_traffic_update = now
            return

        if self._connected:
            self._connected = (now - self._last_activity).total_seconds() < consider_home
            self._ip_address = None

    @property
    def is_connected(self) -> bool:
        return self._connected

    @property
    def interface_type(self) -> DeviceInterfaceType:
        return self._interface_type

    @property
    def mac(self) -> str:
        return self._mac

    @property
    def name(self) -> str | None:
        return self._name

    @property
    def ip_address(self) -> str | None:
        return self._ip_address

    @property
    def last_activity(self) -> datetime:
        return self._last_activity

    @property
    def rx_rate(self) -> int | None:
        return self._rx_rate

    @property
    def tx_rate(self) -> int | None:
        return self._tx_rate

    @property
    def is_known(self) -> bool:
        return self._is_known

    @is_known.setter
    def is_known(self, value: bool) -> None:
        self._is_known = value
