DOMAIN = "ha_glinet"
API_PATH = "/rpc"
INTEGRATION_NAME = "GL-INet"
DEFAULT_URL = "http://192.168.8.1"
DEFAULT_USERNAME = "root"
DEFAULT_PASSWORD = "ChangeMe!"
CONF_TITLE = "title"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_ENABLED_FEATURES = "enabled_features"
CONF_ADD_ALL_DEVICES = "add_all_devices"
CONF_CLEANUP_DEVICES = "cleanup_devices"
CONF_WAN_STATUS_MONITORS = "wan_status_monitors"

WAN_INTERFACE_NAMES = {
    "wan": "Ethernet 1",
    "wwan": "Repeater",
    "tethering": "Tethering",
    "modem_0001": "Cellular",
    "secondwan": "Ethernet 2",
}

FEATURE_CELLULAR = "cellular"
FEATURE_REPEATER = "repeater"
FEATURE_SMS = "sms"
FEATURE_TAILSCALE = "tailscale"
FEATURE_WG_CLIENT = "wg_client"
FEATURE_WG_SERVER = "wg_server"
FEATURE_OVPN_CLIENT = "ovpn_client"
FEATURE_OVPN_SERVER = "ovpn_server"
FEATURE_ZEROTIER = "zerotier"
FEATURE_ADGUARD = "adguard"
FEATURE_LED = "led"
FEATURE_FIREWALL = "firewall"
FEATURE_OPTIONS = [
    FEATURE_CELLULAR,
    FEATURE_REPEATER,
    FEATURE_SMS,
    FEATURE_TAILSCALE,
    FEATURE_WG_CLIENT,
    FEATURE_WG_SERVER,
    FEATURE_OVPN_CLIENT,
    FEATURE_OVPN_SERVER,
    FEATURE_ZEROTIER,
    FEATURE_FIREWALL,
]

SERVICE_GET_SMS = "get_sms"
SERVICE_REMOVE_SMS = "remove_sms"
SERVICE_REFRESH_SMS = "refresh_sms"
SERVICE_SEND_SMS = "send_sms"

SERVICE_SCAN_WIFI = "scan_wifi"
SERVICE_CONNECT_WIFI = "connect_wifi"
SERVICE_DISCONNECT_WIFI = "disconnect_wifi"
SERVICE_GET_SAVED_NETWORKS = "get_saved_networks"
SERVICE_REMOVE_SAVED_NETWORK = "remove_saved_network"
SERVICE_SET_FAN_TEMPERATURE = "set_fan_temperature"

SERVICE_ADD_FIREWALL_RULE = "add_firewall_rule"
SERVICE_REMOVE_FIREWALL_RULE = "remove_firewall_rule"
SERVICE_ADD_PORT_FORWARD = "add_port_forward"
SERVICE_REMOVE_PORT_FORWARD = "remove_port_forward"
SERVICE_SET_DMZ = "set_dmz"

ATTR_MESSAGE_ID = "message_id"
ATTR_SCOPE = "scope"
ATTR_RECIPIENT = "recipient"
ATTR_TEXT = "text"

ATTR_SSID = "ssid"
ATTR_PASSWORD = "password"
ATTR_REMEMBER = "remember"
ATTR_BSSID = "bssid"
ATTR_ALL_BAND = "all_band"
ATTR_DFS = "dfs"
ATTR_TEMPERATURE = "temperature"

ATTR_ENABLED = "enabled"
ATTR_DEST_IP = "dest_ip"
ATTR_RULE_ID = "rule_id"
ATTR_REMOVE_ALL = "remove_all"
ATTR_SRC = "src"
ATTR_SRC_IP = "src_ip"
ATTR_SRC_MAC = "src_mac"
ATTR_SRC_PORT = "src_port"
ATTR_PROTO = "proto"
ATTR_DEST = "dest"
ATTR_DEST_PORT = "dest_port"
ATTR_TARGET = "target"
ATTR_SRC_DPORT = "src_dport"
ATTR_NAME = "name"
