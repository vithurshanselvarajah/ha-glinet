# Triggers

This integration does **not** provide any custom trigger platform (e.g. integration-level event triggers or device automations of its own).

You can still build automations that react to GL.iNet router state by using **state triggers** on the entities the integration exposes — for example, trigger when the `binary_sensor.repeater_connected` state changes, or when a `sensor.fan_speed` crosses a threshold. For a full list of entities, see the [Entity Reference](entities.md).

A ready-made pattern is also available for SMS events using Home Assistant's built-in `time_pattern` trigger — see [Automation Templates → SMS Notification](automation-sms-notification.md).

## Examples

### State trigger on repeater connection

```yaml
trigger:
  - platform: state
    entity_id: binary_sensor.repeater_connected
    to: "on"
action:
  - action: notify.mobile_app
    data:
      title: "Repeater connected"
      message: "WiFi repeater is now online"
```

### Numeric state trigger on fan speed

```yaml
trigger:
  - platform: numeric_state
    entity_id: sensor.fan_speed
    above: 4000
action:
  - action: logbook.log
    data:
      name: "Router fan"
      message: "Fan speed exceeded 4000 RPM"
```

## Related Pages

- [Conditions](conditions.md)
- [Services & Actions parent page](services.md)
