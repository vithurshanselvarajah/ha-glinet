# Parental Control (Optional Feature)

The **Parental Control** feature exposes the GL.iNet router's parental control system to Home Assistant: group switches, per-client group assignment, the router's filtering mode, temporary overrides, and signature database updates.

## Setup Configuration

To enable this feature, check the **Parental & Access Control** option under **Enabled Features** in the integration configuration or options flow.

- **Option key**: `parental_control`

## Binary Sensors

| Entity | Description | API Source |
| --- | --- | --- |
| **Parental control group override** | One diagnostic binary sensor per parental group. `True` when a temporary override is currently active for that group. | `parental-control/get_status` |

## Selects

| Entity | Description | API Source |
| --- | --- | --- |
| **Parental control group** | One select per tracked client device. Allows assigning the client to a parental group/profile, or `None` to remove group membership. Attached to the client MAC device. | `parental-control/get_config` |

## Switches

| Entity | Description | API Source |
| --- | --- | --- |
| **Parental control** | Global switch to enable or disable all parental control features on the router. | `parental-control/set_config` |
| **Parental control group** | One switch per parental control group. Enables or disables internet access limits for that group. | `parental-control/set_group` |

## Actions (Services)

The following services are registered under the `glinet_router` domain when the Parental & Access Control feature is enabled:

### `parental_control_set_temporary_override`

Enables or disables a temporary parental control override for a specific group.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `group_id` | string | Yes | Parental group ID (e.g., `group7342748`). |
| `enabled` | boolean | Yes | Whether to enable the override. |
| `rule_id` | string | Yes | Rule to apply (e.g., `drop`). |
| `duration` | string | No | Duration string (e.g., `01:00:00`). |
| `mac` | string | No | Target a specific router by MAC address. |

### `parental_control_set_filtering_mode`

Sets the router's parental control filtering mode.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `mode` | integer | Yes | Numeric filtering mode value. |
| `mac` | string | No | Target a specific router by MAC address. |

### `parental_control_update_signatures`

Triggers a parental control signature database update on the router.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `mac` | string | No | Target a specific router by MAC address. |

### `parental_control_set_group_schedules`

Enables or bypasses configured schedules for a parental control group.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `group_id` | string | Yes | Router parental group ID. |
| `enabled` | boolean | Yes | Whether schedules should be enforced. |
| `mac` | string | No | Target a specific router by MAC address. |

## Related Pages

- [Access Control](access-control.md) — Blacklist/whitelist internet access control per device.
- [Parental & Access Control parent page](parental-control.md)
