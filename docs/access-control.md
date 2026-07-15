# Access Control (Optional Feature)

The **Access Control** feature lets you block or unblock individual client devices on your network, switch the access control mode between a blacklist and a whitelist, and view per-client internet access state.

## Setup Configuration

To enable this feature, check the **Parental & Access Control** option under **Enabled Features** in the integration configuration or options flow.

- **Option key**: `parental_control`

## Switches

| Entity | Description | API Source |
| --- | --- | --- |
| **Internet access** | One switch per tracked client device. Turning it off blocks that client's internet access; turning it on restores it. | `black_white_list/set_single_mac` |

## Actions (Services)

The following services are registered under the `glinet_router` domain when the Parental & Access Control feature is enabled:

### `access_control_set_mode`

Switches device access control between blacklist and whitelist modes.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `mode` | string | Yes | `black` (blacklist) or `white` (whitelist). |
| `mac` | string | No | Target a specific router by MAC address. |

### `access_control_set_device_block`

Blocks or unblocks a specific client device by MAC address.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `src_mac` | string | Yes | Client MAC address. |
| `block` | boolean | Yes | Whether internet access should be blocked. |
| `mac` | string | No | Target a specific router by MAC address. |

## Related Pages

- [Parental Control](parental-control.md) — Group switches, filtering mode, overrides, and signature updates.
- [Parental & Access Control parent page](parental-control.md)
