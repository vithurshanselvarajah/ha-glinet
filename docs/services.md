# Services (`services.py`)

The integration registers several services under the `ha_glinet` domain to allow manual interaction with the router.

## Registered Services

### `send_sms`
Sends an SMS message.
- **`recipient`**: The full phone number including country code.
- **`text`**: The message content.
- **`mac`** (Optional): Target a specific router by MAC address.

> Note: Messages longer than 160 characters are automatically split into multiple SMS messages and sent sequentially.

### `get_sms`
Retrieves the list of SMS messages currently stored on the router. This service supports response data.
- **`mac`** (Optional): Target a specific router by MAC address.

**Response Format**:
Returns a `messages` array containing SMS details:
- `id`: Unique message identifier.
- `phone_number`: The sender/recipient phone number.
- `direction`: Message direction (`"incoming"`, `"outgoing"`, or `"unknown"`).
- `status`: Human-readable status (e.g., `"Unread"`, `"Sent"`, `"Failed"`).
- `text`: Message content.
- `timestamp`: Message timestamp (if available).

### `remove_sms`
Deletes SMS messages from the router based on a specified scope or ID.
- **`scope`**: The range of messages to remove. Common values:
    - `10`: Specified single SMS (requires `message_id`).
    - `11`: All SMS.
    - `0`: All unread SMS.
    - `1`: All read SMS.
- **`message_id`** (Optional): The unique identifier of the message (found in the `Text messages` sensor attributes). Required if scope is `10`.
- **`mac`** (Optional): Target a specific router by MAC address.

### `refresh_sms`
Manually triggers a poll for new SMS messages.
- **`mac`** (Optional): Target a specific router by MAC address.

### `scan_wifi`
Scans available WiFi networks for repeater mode.
- **`mac`** (Optional): Target a specific router by MAC address.
- **`refresh`** (Optional): Force a fresh router scan instead of using cached scan results.
- **`all_band`** (Optional): Compatibility alias that requests a fresh router scan.
- **`dfs`** (Optional): Compatibility alias that requests a fresh router scan.

**Response Format**:
Returns a `networks` array containing:
- `ssid`
- `bssid`
- `signal`
- `band`
- `channel`
- `encryption` (description)
- `saved`

### `connect_wifi`
Connects the router to an open or secured external WiFi network in repeater mode.
- **`ssid`**: Network name to connect to.
- **`password`** (Optional): Network passphrase. Required for secured networks; omit or leave empty for open networks.
- **`remember`** (Optional): Save network credentials for auto-reconnect. Defaults to `true`.
- **`bssid`** (Optional): Lock connection to a specific AP MAC.
- **`mac`** (Optional): Target a specific router by MAC address.

Example secured-network action:

```yaml
action: ha_glinet.connect_wifi
data:
  ssid: CampgroundWiFi
  password: !secret campground_wifi_password
  remember: true
```

The integration sends the documented GL.iNet repeater defaults for DHCP client mode (`manual: false`, `protocol: dhcp`, `disguise: false`, and `auto_portal: false`) and only includes password/BSSID parameters when they are provided.

### `disconnect_wifi`
Disconnects the router from the current external WiFi repeater network.
- **`mac`** (Optional): Target a specific router by MAC address.

### `get_saved_networks`
Retrieves saved repeater WiFi networks from the router.
- **`mac`** (Optional): Target a specific router by MAC address.

### `remove_saved_network`
Removes a saved repeater WiFi network from the router.
- **`ssid`**: The SSID of the network to remove.
- **`mac`** (Optional): Target a specific router by MAC address.

### `set_fan_temperature`
Sets the temperature threshold at which the router's fan will start running.
- **`temperature`**: Target threshold temperature in Celsius (typically 70-90).
- **`mac`** (Optional): Target a specific router by MAC address.

### `add_firewall_rule`
Adds a custom firewall rule.
- **`name`**: Descriptive name for the rule.
- **`src`**: Source zone (e.g., `wan`, `lan`).
- **`src_ip`** (Optional): Source IP address.
- **`src_mac`** (Optional): Source MAC address.
- **`src_port`** (Optional): Source port.
- **`proto`**: Protocol (`tcp`, `udp`, `tcpudp`).
- **`dest`**: Destination zone.
- **`dest_ip`** (Optional): Destination IP address.
- **`dest_port`** (Optional): Destination port.
- **`target`**: Target action (`ACCEPT`, `DROP`, `REJECT`).
- **`enabled`**: Whether the rule is active.
- **`mac`** (Optional): Target a specific router by MAC address.

### `remove_firewall_rule`
Removes a firewall rule.
- **`rule_id`**: The ID of the rule to remove.
- **`mac`** (Optional): Target a specific router by MAC address.

### `get_firewall_rules`
Returns configured firewall rules as action response data.
- **Response**: `rules`, each containing `id` and `name`.
- **`mac`** (Optional): Target a specific router by MAC address.

### `add_port_forward`
Adds a port forwarding rule.
- **`name`**: Descriptive name.
- **`src`**: Source zone (usually `wan`).
- **`src_dport`**: External port.
- **`proto`**: Protocol.
- **`dest`**: Destination zone (usually `lan`).
- **`dest_ip`**: Internal IP address.
- **`dest_port`**: Internal port.
- **`enabled`**: Whether the rule is active.
- **`mac`** (Optional): Target a specific router by MAC address.

### `remove_port_forward`
Removes a port forwarding rule.
- **`rule_id`** (Optional): The ID of the rule to remove.
- **`remove_all`** (Optional): If true, removes all port forwards.
- **`mac`** (Optional): Target a specific router by MAC address.

### `set_dmz`
Configures DMZ (DeMilitarized Zone) settings.
- **`enabled`**: Whether DMZ is enabled.
- **`dest_ip`** (Optional): The internal IP address to expose.
- **`mac`** (Optional): Target a specific router by MAC address.

### `get_mcu_battery_config`
Returns MCU battery warning configuration as action response data.
- **Response**: Router `capacity`, `temp_high`, and `temp_low` warning config.
- **`mac`** (Optional): Target a specific router by MAC address.

### `set_mcu_battery_config`
Sets MCU battery warning configuration.
- **`capacity_enabled`**: Whether low-capacity warning is enabled.
- **`capacity`**: Low-capacity warning percentage.
- **`temp_high_enabled`**: Whether high-temperature warning is enabled.
- **`temp_high`**: High-temperature warning threshold in Celsius.
- **`temp_low_enabled`**: Whether low-temperature warning is enabled.
- **`temp_low`**: Low-temperature warning threshold in Celsius.
- **`mac`** (Optional): Target a specific router by MAC address.

### `get_mcu_oled_config`
Returns MCU OLED screen display configuration as action response data.
- **Response**: Router `screen_display` config.
- **`mac`** (Optional): Target a specific router by MAC address.

### `set_mcu_oled_config`
Updates MCU OLED screen display sections. Omitted fields keep their current router values.
- **`main`**, **`wifi_password`**, **`wifi_2g`**, **`wifi_5g`**, **`lan`**, **`vpn`**, **`custom`** (Optional): Display toggles.
- **`content`** (Optional): Custom display command/content.
- **`mac`** (Optional): Target a specific router by MAC address.

### `parental_control_set_temporary_override`
Enables or disables a parental control brief/temporary override for a group.
- **`group_id`**: Router parental group ID, such as `group7342748`.
- **`enabled`**: Whether to enable the override.
- **`rule_id`**: Rule to apply, such as `drop`.
- **`duration`** (Optional): Router duration string, for example `01:00:00`.
- **`mac`** (Optional): Target a specific router by MAC address.

### `parental_control_set_filtering_mode`
Sets the router parental control filtering mode.
- **`mode`**: Numeric router mode value.
- **`mac`** (Optional): Target a specific router by MAC address.

### `parental_control_update_signatures`
Triggers a parental control signature database update on the router.
- **`mac`** (Optional): Target a specific router by MAC address.

### `access_control_set_mode`
Switches device access control between blacklist and whitelist modes.
- **`mode`**: `black` or `white`.
- **`mac`** (Optional): Target a specific router by MAC address.

### `access_control_set_device_block`
Blocks or unblocks a specific client MAC address.
- **`src_mac`**: Client MAC address.
- **`block`**: Whether internet access should be blocked.
- **`mac`** (Optional): Target a specific router by MAC address.

### `parental_control_set_group_schedules`
Enables or bypasses schedules for a parental control group.
- **`group_id`**: Router parental group ID.
- **`enabled`**: Whether schedules should be enforced.
- **`mac`** (Optional): Target a specific router by MAC address.

> Note: Firewall, repeater, SMS, MCU battery, MCU OLED, and parental/access services are only registered when the corresponding support is enabled for at least one router.

## Internal Logic

| Function | Purpose |
| --- | --- |
| `async_register_services` | Entry point during integration setup to register the domain services. |
| `_get_hub` | Helper to find the active `GLinetHub` instance matching the provided MAC address. |
