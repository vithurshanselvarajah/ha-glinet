from .adguard import AdGuardModule
from .black_white_list import BlackWhiteListModule
from .clients import ClientsModule
from .diag import DiagModule
from .fan import FanModule
from .firewall import FirewallModule
from .kmwan import KmwanModule
from .led import LedModule
from .macclone import MacCloneModule
from .mcu import McuModule
from .modem import ModemModule
from .mwan3 import Mwan3Module
from .ovpn_client import OvpnClientModule
from .ovpn_server import OvpnServerModule
from .parental_control import ParentalControlModule
from .repeater import RepeaterModule
from .system import SystemModule
from .tailscale import TailscaleModule
from .upgrade import UpgradeModule
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
    "KmwanModule",
    "LedModule",
    "MacCloneModule",
    "McuModule",
    "ModemModule",
    "Mwan3Module",
    "OvpnClientModule",
    "OvpnServerModule",
    "ParentalControlModule",
    "RepeaterModule",
    "SystemModule",
    "TailscaleModule",
    "UpgradeModule",
    "VpnClientModule",
    "WgClientModule",
    "WgServerModule",
    "WifiModule",
    "WireGuardModule",
    "ZeroTierModule",
]
