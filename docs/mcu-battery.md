# MCU Battery (Optional Feature)

The **MCU Battery** feature enables battery status monitoring and warning threshold configuration for GL.iNet travel routers with a built-in battery.

## Setup Configuration

To enable this feature, check the **MCU Battery** option under **Enabled Features** in the integration configuration or options flow.

- **Option key**: `mcu_battery`

> Disabling this feature removes all battery sensors from the registry.

## Exposed Entities

### Sensors

| Entity | Description | API Source |
| --- | --- | --- |
| **Battery temperature** | Current battery temperature in Celsius. | `system/get_status` MCU data |
| **Battery charge** | Battery charge percentage. Extra attributes include charge count, fast-charge status, and abnormal type. | `system/get_status` MCU data |
| **Battery charging status** | Current charging state — `charging` when `charging_status` is `1`, `not_charging` when it is `0`. | `system/get_status` MCU data |

### Binary Sensors

| Entity | Description | API Source |
| --- | --- | --- |
| **Battery abnormal** | Diagnostic binary sensor — `True` when the MCU reports an abnormal status flag. | `system/get_status` MCU data |

## Actions (Services)

The following services are registered under the `glinet_router` domain when the MCU Battery feature is enabled:

### `get_mcu_battery_config`

Retrieves the current battery warning configuration from the router. Supports response data.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `mac` | string | No | Target a specific router by MAC address. |

**Response**: Returns current warning thresholds for `capacity`, `temp_high`, and `temp_low`, including whether each is enabled.

### `set_mcu_battery_config`

Sets the battery warning configuration parameters.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `capacity_enabled` | boolean | Yes | Toggles low-capacity warnings. |
| `capacity` | integer (1-100) | Yes | Low-capacity warning percentage threshold. |
| `temp_high_enabled` | boolean | Yes | Toggles high-temperature warnings. |
| `temp_high` | integer | Yes | High-temperature warning threshold in Celsius. |
| `temp_low_enabled` | boolean | Yes | Toggles low-temperature warnings. |
| `temp_low` | integer | Yes | Low-temperature warning threshold in Celsius. |
| `mac` | string | No | Target a specific router by MAC address. |

## Related Pages

- [Services & Actions](services.md) — How to use Home Assistant services with this integration.
- [Entity Reference](entities.md) — All core and optional entities.
