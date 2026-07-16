# Conditions

This integration does **not** provide any custom condition platform (e.g. integration-level conditions that wrap router state).

You can use Home Assistant's built-in conditions in your automations, such as `state`, `template`, `numeric_state`, or `time`, against the entities this integration exposes. For example, condition a notification on the `binary_sensor.repeater_connected` entity, or on a `sensor.cpu_temp` value.

## Examples

### State condition

```yaml
condition:
  - condition: state
    entity_id: binary_sensor.repeater_connected
    state: "on"
```

### Numeric state condition

```yaml
condition:
  - condition: numeric_state
    entity_id: sensor.cpu_temp
    above: 70
```

## Related Pages

- [Triggers](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/triggers)
- [Services & Actions parent page](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/services)
