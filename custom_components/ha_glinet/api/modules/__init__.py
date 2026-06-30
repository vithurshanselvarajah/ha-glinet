from .adguard import AdGuardModule
from .black_white_list import BlackWhiteListModule
from .clients import ClientsModule
from .diag import DiagModule
from .fan import FanModule
from .firewall import FirewallModule
from .led import LedModule
from .macclone import MacCloneModule
from .mcu import McuModule
from .kmwan import KmwanModule
from .mwan3 import Mwan3Module
from .modem import ModemModule
from .ovpn_client import OvpnClientModule
from .ovpn_server import OvpnServerModule
from .parental_control import ParentalControlModule
from .repeater import RepeaterModule
from .system import SystemModule
from .tailscale import TailscaleModule
from .wg_client import VpnClientModule, WgClientModule, WireGuardModule
from .wg_server import WgServerModule
from .wifi import WifiModule
from .zerotier import ZeroTierModule

__all__ = [
    "AdGuardModule",
    "BlackWhiteListModule",
    "ClientsModule",
    "DiagModule",
    "FanModule",
    "FirewallModule",
    "LedModule",
    "MacCloneModule",
    "McuModule",
    "KmwanModule",
    "Mwan3Module",
    "ModemModule",
    "OvpnClientModule",
    "OvpnServerModule",
    "ParentalControlModule",
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
