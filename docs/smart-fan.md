# Smart Fan (Optional Feature)

Some GL.iNet routers expose fan status and threshold settings through the device API. When that data is available, the integration surfaces it in Home Assistant.

## Setup Configuration

The fan feature does not require a separate option to be enabled. It is available automatically when the router reports fan data through the API.

## Exposed Entities

| Entity | Type | Description | API Source |
| --- | --- | --- | --- |
| **Fan status** | `binary_sensor` | Whether the fan is currently running. | `fan/get_status` |
| **Fan speed** | `sensor` | Current fan speed in RPM. Includes `running` and `temperature_threshold` attributes when supported. | `fan/get_status` |
| **Fan threshold temperature** | `sensor` | Configured temperature at which the fan starts, in °C (read-only display). | `fan/get_config` |

> The fan trigger temperature cannot be changed from a `number` entity. Use the `set_fan_temperature` service below to update the threshold.

## Actions (Services)

The following service is registered under the `glinet_router` domain:

### `set_fan_temperature`

Sets the router's fan trigger temperature.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `temperature` | integer (70-90) | Yes | New trigger temperature in Celsius. |
| `mac` | string | No | Target a specific router by MAC address. |

Example:

```yaml
action: glinet_router.set_fan_temperature
data:
  temperature: 75
```

## Related Pages

- [Services & Actions](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/services) — How to use Home Assistant services with this integration.
- [Entity Reference](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/entities) — All core and optional entities.
