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
- **`all_band`** (Optional): Scan all radio bands.
- **`dfs`** (Optional): Include DFS channels in the scan.

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
Connects the router to an external WiFi network in repeater mode.
- **`ssid`**: Network name to connect to.
- **`password`** (Optional): Network passphrase.
- **`remember`** (Optional): Save network credentials for auto-reconnect. Defaults to `true`.
- **`bssid`** (Optional): Lock connection to a specific AP MAC.
- **`mac`** (Optional): Target a specific router by MAC address.

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
- **`rule_id`** (Optional): The ID of the rule to remove.
- **`remove_all`** (Optional): If true, removes all custom rules.
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

> Note: Firewall and repeater services are only registered when the corresponding support is enabled for the router.

## Internal Logic

| Function | Purpose |
| --- | --- |
| `async_register_services` | Entry point during integration setup to register the domain services. |
| `_get_hub` | Helper to find the active `GLinetHub` instance matching the provided MAC address. |
