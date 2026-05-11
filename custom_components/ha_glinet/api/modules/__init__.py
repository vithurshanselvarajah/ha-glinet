from .clients import ClientsModule
from .diag import DiagModule
from .fan import FanModule
from .led import LedModule
from .macclone import MacCloneModule
from .modem import ModemModule
from .repeater import RepeaterModule
from .system import SystemModule
from .tailscale import TailscaleModule
from .wg_client import VpnClientModule, WgClientModule, WireGuardModule
from .wg_server import WgServerModule
from .wifi import WifiModule

__all__ = [
    "ClientsModule",
    "DiagModule",
    "FanModule",
    "LedModule",
    "MacCloneModule",
    "ModemModule",
    "RepeaterModule",
    "SystemModule",
    "TailscaleModule",
    "VpnClientModule",
    "WgClientModule",
    "WgServerModule",
    "WifiModule",
    "WireGuardModule",
]
