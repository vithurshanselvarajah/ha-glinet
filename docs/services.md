# Services (`services.py`)

The integration registers several services under the `ha_glinet` domain to allow manual interaction with the router.

## Registered Services

### `send_sms`
Sends an SMS message.
- **`recipient`**: The full phone number including country code.
- **`text`**: The message content.
- **`mac`** (Optional): Target a specific router by MAC address.

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

> Note: Repeater services are only registered when the router entry has repeater support enabled.

## Internal Logic

| Function | Purpose |
| --- | --- |
| `async_register_services` | Entry point during integration setup to register the domain services. |
| `_get_hub` | Helper to find the active `GLinetHub` instance matching the provided MAC address. |
