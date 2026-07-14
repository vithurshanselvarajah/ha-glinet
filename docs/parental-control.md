# Parental & Access Control (Optional Feature)

The **Parental & Access Control** feature enables per-client internet access switches, parental group assignment, router-level parental controls, temporary overrides, and signature database updates.

## Setup Configuration

To enable this feature, check the **Parental & Access Control** option under **Enabled Features** in the integration configuration or options flow.

- **Option key**: `parental_control`

---

## Exposed Entities

### Binary Sensors

| Entity | Description | API Source |
| --- | --- | --- |
| **Parental control group override** | One diagnostic binary sensor per parental group. `True` when a temporary brief/override is currently active for that group. | `parental-control/get_status` |

### Selects

| Entity | Description | API Source |
| --- | --- | --- |
| **Parental control group** | One select per tracked client device. Allows assigning the client to a parental group/profile, or `None` to remove group membership. Attached to the client MAC device. | `parental-control/get_config` |

### Switches

| Entity | Description | API Source |
| --- | --- | --- |
| **Parental control** | Global switch to enable or disable all parental control features on the router. | `parental-control/set_config` |
| **Parental control group** | One switch per parental control group. Enables or disables internet access limits for that group. | `parental-control/set_group` |
| **Internet access** | One switch per tracked client device. Turning it off blocks that client's internet access; turning it on restores it. | `black_white_list/set_single_mac` |

---

## Actions (Services)

The following services are registered under the `glinet_router` domain when the Parental & Access Control feature is enabled:

### `parental_control_set_temporary_override`
Enables or disables a temporary parental control override for a specific group.

- **`group_id`**: Parental group ID (e.g., `group7342748`).
- **`enabled`**: Whether to enable the override.
- **`rule_id`**: Rule to apply (e.g., `drop`).
- **`duration`** (Optional): Duration string (e.g., `01:00:00`).
- **`mac`** (Optional): Target a specific router by MAC address.

### `parental_control_set_filtering_mode`
Sets the router's parental control filtering mode.

- **`mode`**: Numeric filtering mode value.
- **`mac`** (Optional): Target a specific router by MAC address.

### `parental_control_update_signatures`
Triggers a parental control signature database update on the router.

- **`mac`** (Optional): Target a specific router by MAC address.

### `access_control_set_mode`
Switches device access control between blacklist and whitelist modes.

- **`mode`**: `black` (blacklist) or `white` (whitelist).
- **`mac`** (Optional): Target a specific router by MAC address.

### `access_control_set_device_block`
Blocks or unblocks a specific client device by MAC address.

- **`src_mac`**: Client MAC address.
- **`block`**: Whether internet access should be blocked.
- **`mac`** (Optional): Target a specific router by MAC address.

### `parental_control_set_group_schedules`
Enables or bypasses configured schedules for a parental control group.

- **`group_id`**: Router parental group ID.
- **`enabled`**: Whether schedules should be enforced.
- **`mac`** (Optional): Target a specific router by MAC address.
