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

## Internal Logic

| Function | Purpose |
| --- | --- |
| `async_register_services` | Entry point during integration setup to register the domain services. |
| `_get_hub` | Helper to find the active `GLinetHub` instance matching the provided MAC address. |
