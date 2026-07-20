# SMS (Optional Feature)

The **SMS** feature enables the text message inbox sensor and actions for sending and managing SMS messages on routers with an active mobile connection.

## Setup Configuration

To enable this feature, check the **SMS** option under **Enabled Features** in the integration configuration or options flow.

- **Option key**: `sms`

## Exposed Entities

### Sensors

| Entity | Description | API Source |
| --- | --- | --- |
| **Unread messages** | Count of unread SMS messages (status `0`) currently stored on the SIM card/modem. Attributes include `unread_count`, `message_count`, `incoming_count`, `outgoing_count`, and a full `messages` list with per-message details. | `modem/get_sms_list` |

The `messages` attribute contains objects with the following fields:

| Field | Description |
| --- | --- |
| `id` | Unique message identifier. |
| `phone_number` | The sender or recipient phone number. |
| `direction` | `incoming`, `outgoing`, or `unknown`. |
| `status` | Human-readable status (e.g., `Unread`, `Sent`, `Failed`). |
| `text` | Message body. |
| `timestamp` | Message timestamp (if available). |

## Actions (Services)

The following services are registered under the `glinet_router` domain when the SMS feature is enabled:

### `send_sms`

Sends a text message.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `recipient` | string | Yes | The destination phone number including country code. |
| `text` | string | Yes | The message body. Messages longer than 160 characters are automatically split and sent sequentially. |
| `mac` | string | No | Target a specific router by MAC address. |

### `get_sms`

Retrieves the list of SMS messages currently stored on the router. Supports response data.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `mac` | string | No | Target a specific router by MAC address. |

**Response Format**: Returns a `messages` array (same structure as the sensor attributes above).

### `remove_sms`

Deletes SMS messages from the router based on a scope or specific ID.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `scope` | integer | Yes | The deletion scope: `10` — Specific single SMS (requires `message_id`). `11` — All SMS. `0` — All unread SMS. `1` — All read SMS. |
| `message_id` | string | No | The unique ID of the message to delete. Found in the `Unread messages` sensor attributes. Required if `scope` is `10`. |
| `mac` | string | No | Target a specific router by MAC address. |

### `refresh_sms`

Manually triggers a poll for new SMS messages.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `mac` | string | No | Target a specific router by MAC address. |

## Related Pages

- [Services & Actions](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/services) — How to use Home Assistant services with this integration.
- [Entity Reference](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/entities) — All core and optional entities.
