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

FEATURE_CELLULAR = "cellular"
FEATURE_REPEATER = "repeater"
FEATURE_SMS = "sms"
FEATURE_TAILSCALE = "tailscale"
FEATURE_WG_CLIENT = "wg_client"
FEATURE_WG_SERVER = "wg_server"
FEATURE_OVPN_CLIENT = "ovpn_client"
FEATURE_OVPN_SERVER = "ovpn_server"
FEATURE_OPTIONS = [
    FEATURE_CELLULAR,
    FEATURE_REPEATER,
    FEATURE_SMS,
    FEATURE_TAILSCALE,
    FEATURE_WG_CLIENT,
    FEATURE_WG_SERVER,
    FEATURE_OVPN_CLIENT,
    FEATURE_OVPN_SERVER,
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
