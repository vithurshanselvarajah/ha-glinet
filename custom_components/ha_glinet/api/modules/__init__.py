from .system import SystemModule
from .modem import ModemModule
from .wifi import WifiModule
from .clients import ClientsModule
from .vpn import WireGuardModule, VpnClientModule, VpnModule
from .tailscale import TailscaleModule
from .repeater import RepeaterModule
from .fan import FanModule
from .led import LedModule
from .macclone import MacCloneModule
from .diag import DiagModule

__all__ = [
    "SystemModule",
    "ModemModule",
    "WifiModule",
    "ClientsModule",
    "WireGuardModule",
    "VpnClientModule",
    "VpnModule",
    "TailscaleModule",
    "RepeaterModule",
    "FanModule",
    "LedModule",
    "MacCloneModule",
    "DiagModule",
]
