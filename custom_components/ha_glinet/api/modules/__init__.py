from .clients import ClientsModule
from .diag import DiagModule
from .fan import FanModule
from .led import LedModule
from .macclone import MacCloneModule
from .modem import ModemModule
from .ovpn_client import OvpnClientModule
from .ovpn_server import OvpnServerModule
from .repeater import RepeaterModule
from .system import SystemModule
from .tailscale import TailscaleModule
from .wg_client import VpnClientModule, WgClientModule, WireGuardModule
from .wg_server import WgServerModule
from .wifi import WifiModule
from .zerotier import ZeroTierModule

__all__ = [
    "ClientsModule",
    "DiagModule",
    "FanModule",
    "LedModule",
    "MacCloneModule",
    "ModemModule",
    "OvpnClientModule",
    "OvpnServerModule",
    "RepeaterModule",
    "SystemModule",
    "TailscaleModule",
    "VpnClientModule",
    "WgClientModule",
    "WgServerModule",
    "WifiModule",
    "WireGuardModule",
    "ZeroTierModule",
]
