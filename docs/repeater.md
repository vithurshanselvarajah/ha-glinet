# Repeater (Optional Feature)

The **Repeater** feature enables WiFi station mode management, AP scanning, connection control, and saved network management.

## Setup Configuration

To enable this feature, check the **Repeater** option under **Enabled Features** in the integration configuration or options flow.

- **Option key**: `repeater`

## Exposed Entities

### Sensors

| Entity | Description | API Source |
| --- | --- | --- |
| **Repeater state** | Current repeater connection state (e.g., `connected`, `connecting`, `disconnected`, `initializing`, `wan_available`). | `repeater/get_status` |
| **Repeater SSID** | SSID of the connected external WiFi network. Available while connecting, connected, or WAN available. | `repeater/get_status` |
| **Repeater signal** | Signal strength in dBm of the repeater connection. Available while connecting, connected, or WAN available. | `repeater/get_status` |
| **Repeater channel** | Enum sensor indicating the connected WiFi band. Converts the raw channel number to a band key: `2_4ghz` (channels 1–14) or `5ghz` (channels 36–177). | `repeater/get_status` |
| **Repeater IP address** | The IP address assigned to the repeater interface. Available only when connected or WAN available. | `repeater/get_status` |
| **Repeater gateway** | The gateway IP address of the repeater interface. Available only when connected or WAN available. | `repeater/get_status` |
| **Repeater DNS** | Primary DNS server IP address. Additional servers are listed in the `dns_servers` attribute. Available only when connected or WAN available. | `repeater/get_status` |
| **Repeater BSSID** | MAC address of the connected access point. Available while connecting, connected, or WAN available. | `repeater/get_status` |

The **Repeater state** sensor remains available whenever the repeater feature is enabled so it can report states including `initializing` and `wan_available`. Connection detail sensors become unavailable when the repeater is off or failed, which avoids stale SSID/IP/DNS values after a disconnect.

### Binary Sensors

| Entity | Description | API Source |
| --- | --- | --- |
| **Repeater connected** | `True` when the repeater is connected or WAN is available. Attributes include SSID, BSSID, signal, WiFi generation, EAP, and bare mode. | `repeater/get_status` |
| **Repeater bare mode** | `True` when repeater bare mode is active. | `repeater/get_status` |

### Selects

| Entity | Description | API Source |
| --- | --- | --- |
| **WiFi network** | Choose a saved or available WiFi SSID for repeater mode. Options are grouped into "Known" and "Available". | `hub.scanned_networks` |
| **Repeater band** | Controls the locked wireless band (`auto`, `2g`, `5g`) used for repeater scanning and connection. | `repeater/get_config` |

### Switches

| Entity | Description | API Source |
| --- | --- | --- |
| **Repeater auto-switch** | Toggle whether the router automatically switches between saved networks. | `repeater/get_config` / `repeater/set_config` |
| **Repeater bare mode** | Toggle bare mode for the active repeater connection. | `repeater/enter_bare_mode` / `repeater/exit_bare_mode` |
| **Repeater smart reconnect** | Toggle smart reconnection logic. | `repeater/set_config` |

## Actions (Services)

The following services are registered under the `glinet_router` domain when the Repeater feature is enabled:

### `scan_wifi`

Scans available WiFi networks for repeater mode.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `mac` | string | No | Target a specific router by MAC address. |
| `refresh` | boolean | No | Force a fresh scan on the router instead of returning cached results. |
| `all_band` | boolean | No | Compatibility alias that requests a fresh router scan. |
| `dfs` | boolean | No | Compatibility alias that requests a fresh router scan. |

**Response Format**: Returns a `networks` array containing `ssid`, `bssid`, `signal`, `band`, `channel`, `encryption` (description), and `saved` status.

### `connect_wifi`

Connects the router to an open or secured external WiFi network.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `ssid` | string | Yes | SSID of the network to connect to. |
| `password` | string | No | Password for secured networks. Omit for open networks. |
| `remember` | boolean | No | Save credentials for auto-reconnect. Defaults to `true`. |
| `bssid` | string | No | Lock connection to a specific AP MAC address. |
| `mac` | string | No | Target a specific router by MAC address. |

Example:

```yaml
action: glinet_router.connect_wifi
data:
  ssid: CampgroundWiFi
  password: !secret campground_wifi_password
  remember: true
```

### `disconnect_wifi`

Disconnects the router from the current external WiFi repeater network.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `mac` | string | No | Target a specific router by MAC address. |

### `get_saved_networks`

Retrieves saved repeater WiFi networks from the router.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `mac` | string | No | Target a specific router by MAC address. |

### `remove_saved_network`

Removes a saved repeater WiFi network from the router.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `ssid` | string | Yes | The SSID of the saved network to remove. |
| `mac` | string | No | Target a specific router by MAC address. |

## Related Pages

- [Services & Actions](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/services) — How to use Home Assistant services with this integration.
- [Entity Reference](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/entities) — All core and optional entities.
