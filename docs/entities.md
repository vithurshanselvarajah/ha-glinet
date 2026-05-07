# Entity Reference (`entities/`)

This integration exposes entities from data fetched through the GL.iNet JSON-RPC API.

## Buttons

| Entity | Source | Notes |
| --- | --- | --- |
| Reboot | `system/reboot` | Reboots the router immediately. |

## Device Trackers

Device trackers are created from online devices returned by the router API **only if the device is already known to Home Assistant** through another integration (e.g., the Mobile App, ESPHome, Zigbee, etc.). 

This behavior prevents the integration from automatically adding every guest device, transient client, or unknown IoT device on your network as a new tracker entity.

If you want to track a specific device that is not yet known to Home Assistant, you must first ensure it is added to the Home Assistant device registry by another means.

The tracker monitors:

- MAC address
- Name/alias
- IP address while online
- Interface type
- Last activity timestamp

Tracked devices use a `consider_home` logic (default 180s) to prevent entities from flickering to "Away" during brief client sleep cycles or router re-polls. Unhelpful tracker entities can be managed via the standard entity settings:

1. Open **Settings**.
2. Open **Devices & services**.
3. Select the GL-INet integration or the tracked device.
4. Open the entity.
5. Use the entity settings menu to disable or delete it.

If a device uses randomized MAC addresses, Home Assistant may see each randomized address as a separate tracker. Disable private/random MAC addressing for that WiFi network when you want stable tracking.

## Sensors

### Router Diagnostics

| Entity | Source | Notes |
| --- | --- | --- |
| CPU temperature | `system/get_status` | Diagnostic sensor, when supported by the router. |
| Load avg (1m) | `system/get_status` | Diagnostic sensor. |
| Load avg (5m) | `system/get_status` | Diagnostic sensor. |
| Load avg (15m) | `system/get_status` | Diagnostic sensor. |
| Memory usage | `system/get_status` | Calculated from total/free memory. |
| Flash usage | `system/get_status` | Calculated from total/free flash. |
| Uptime | `system/get_status` | Timestamp sensor. |

### Internet and Traffic

| Entity | Source | Notes |
| --- | --- | --- |
| Connection status | `hub.internet_status` | Binary connectivity state. |
| Public IP | `hub.internet_status` | The WAN IP address assigned to the router. |
| Connected clients | `clients/get_list` | Count of currently online tracked clients. |

### Cellular and SMS

| Entity | Source | Notes |
| --- | --- | --- |
| Cellular signal | Optional `modem/get_status` | Signal value when the router exposes modem status. |
| Cellular RSSI | Optional `modem/get_status` | Received Signal Strength Indicator in dBm. |
| Cellular RSRP | Optional `modem/get_status` | Reference Signal Received Power in dBm. |
| Cellular RSRQ | Optional `modem/get_status` | Reference Signal Received Quality in dB. |
| Cellular SINR | Optional `modem/get_status` | Signal-to-Interference-plus-Noise Ratio in dB. |
| Cellular band | Optional `modem/get_status` | The active frequency band/service type. |
| Cellular network | Optional `modem/get_status` | Operator/network/mode when available. |
| Text messages | Optional `sms/get_list` | Count of messages. Attributes include `message_count`, `incoming_count`, `outgoing_count`, and a `messages` list with details like `id`, `phone_number`, `direction`, `status`, `text`, and `timestamp`. |

### Repeater (WiFi Station)

| Entity | Source | Notes |
| --- | --- | --- |
| Repeater state | Optional `repeater/get_status` | Current repeater connection state. |
| Repeater SSID | Optional `repeater/get_status` | SSID of the connected external network. |
| Repeater signal | Optional `repeater/get_status` | Signal strength of the repeater connection. |
| Repeater channel | Optional `repeater/get_status` | Channel used by the repeater connection. |
| Repeater IP address | Optional `repeater/get_status` | IP address assigned to the repeater interface. |

### Client Bandwidth

Each tracked client includes real-time bandwidth sensors attached to the client device:

- Download rate
- Upload rate

These sensors are created only when the router reports bandwidth fields in the client list. Rates are calculated based on delta changes between polls if explicit rate fields are missing.

## Selects

| Entity | Source | Notes |
| --- | --- | --- |
| WiFi network | `hub.scanned_networks` | Choose a saved or available WiFi SSID for repeater mode. Groups options by "Known" and "Available". |
| Repeater band | Optional `repeater/get_config` | Controls the locked wireless band used for repeater scanning and connection. |

## Switches

| Entity | Source | Notes |
| --- | --- | --- |
| WiFi interface switches | `wifi/get_config`, `wifi/set_config` | One switch per WiFi interface reported by the router. |
| WireGuard client switches | `wg-client` and `vpn-client` APIs | One switch per WireGuard client config returned by the router. Newer firmware uses `vpn-client`; older firmware uses `wg-client`. |
| Tailscale | `tailscale/get_status`, `tailscale/set_config` | Created when Tailscale is configured. |
| Repeater auto-switch | `repeater/get_config` | Toggle whether the router automatically switches between saved networks. |
