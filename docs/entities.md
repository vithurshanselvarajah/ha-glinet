# Entity Reference (`entities/`)

This integration exposes entities from data fetched through the GL.iNet JSON-RPC API.

## Buttons

| Entity | Source | Notes |
| --- | --- | --- |
| Reboot | `system/reboot` | Reboots the router immediately. |
| Fan test | Optional `fan/test_fan` | Diagnostic button to run the fan at full speed for 10 seconds. |

## Device Trackers

Device trackers are created from online devices returned by the router API **only if the device is already known to Home Assistant** through another integration (e.g., the Mobile App, ESPHome, Zigbee, etc.). 

This behavior prevents the integration from automatically adding every guest device, transient client, or unknown IoT device on your network as a new tracker entity.

However, you can enable the **Discovery unknown devices** option during integration setup or in the options flow. When enabled, the integration will track every device seen by the router, regardless of its status in the Home Assistant device registry. This is useful for monitoring all network activity, but may result in many entities being created.

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
| Fan speed | Optional `fan/get_status` | Diagnostic sensor showing current fan speed in RPM. |
| Fan threshold temperature | Optional `fan/get_config` | Diagnostic sensor showing the current temperature threshold. |

### Internet and Traffic

| Entity | Source | Notes |
| --- | --- | --- |
| WAN IP | Optional `modem/get_status` | The IP address assigned to the internet interface (modem). |
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
| Cellular APN | Optional `modem/get_status` | The Access Point Name used for the cellular connection. |
| Text messages | Optional `sms/get_list` | Count of messages. Attributes include `message_count`, `incoming_count`, `outgoing_count`, and a `messages` list with details like `id`, `phone_number`, `direction`, `status`, `text`, and `timestamp`. |

### Repeater (WiFi Station)

| Entity | Source | Notes |
| --- | --- | --- |
| Repeater state | Optional `repeater/get_status` | Current repeater connection state. |
| Repeater SSID | Optional `repeater/get_status` | SSID of the connected external network. |
| Repeater signal | Optional `repeater/get_status` | Signal strength of the repeater connection. |
| Repeater channel | Optional `repeater/get_status` | Enum sensor showing the WiFi band. See [Channel-to-band mapping](#channel-to-band-mapping) below. |
| Repeater IP address | Optional `repeater/get_status` | IP address assigned to the repeater interface. |
| Repeater gateway | Optional `repeater/get_status` | Default gateway of the repeater interface. |
| Repeater DNS | Optional `repeater/get_status` | Primary DNS server. Additional servers are listed in the `dns_servers` attribute. |
| Repeater BSSID | Optional `repeater/get_status` | MAC address of the connected access point. |

#### Channel-to-band mapping

The **Repeater channel** sensor uses `SensorDeviceClass.ENUM` with a `channel_to_band()` helper (defined in `utils.py`) that converts the raw WiFi channel number into a band key:

| Channel range | Band key | Displayed as |
| --- | --- | --- |
| 1 – 14 | `2_4ghz` | 2.4 GHz |
| 36 – 177 | `5ghz` | 5 GHz |

The raw channel number and band key are also exposed as `channel` and `band` extra state attributes.

### Client Bandwidth

Each tracked client includes real-time bandwidth sensors attached to the client device (listed under the **Diagnostic** category):

- Download rate
- Upload rate

These sensors are created only when the router reports bandwidth fields in the client list. Rates are calculated based on delta changes between polls if explicit rate fields are missing.

### Fan

| Entity | Source | Notes |
| --- | --- | --- |
| Fan status | Optional `fan/get_status` | Binary sensor showing if the fan is currently active. |
| Fan speed | Optional `fan/get_status` | Diagnostic sensor showing current fan speed in RPM. |
| Fan threshold temperature | Optional `fan/get_config` | Diagnostic sensor showing the current temperature threshold. |

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
