# Services & Actions

The integration registers services under the `glinet_router` domain to allow manual interaction with the router from Home Assistant automations and scripts.

Services are registered dynamically based on your **Enabled Features** configuration. If a feature (e.g., SMS) is disabled across all configured routers, its services are automatically removed from Home Assistant to keep the UI clean.

For full parameter details, visit the optional feature page for each service group:

| Service Group | Feature Page |
| --- | --- |
| `send_sms`, `get_sms`, `remove_sms`, `refresh_sms` | [SMS](sms.md) |
| `scan_wifi`, `connect_wifi`, `disconnect_wifi`, `get_saved_networks`, `remove_saved_network` | [Repeater](repeater.md) |
| `add_firewall_rule`, `remove_firewall_rule`, `get_firewall_rules` | [Firewall Rules](firewall-rules.md) |
| `add_port_forward`, `remove_port_forward` | [Port Forwards](port-forwards.md) |
| `set_dmz` | [DMZ](dmz.md) |
| `get_mcu_battery_config`, `set_mcu_battery_config` | [MCU Battery](mcu-battery.md) |
| `get_mcu_oled_config`, `set_mcu_oled_config` | [MCU OLED](mcu-oled.md) |
| `kmwan_get_config`, `kmwan_get_status`, `kmwan_set_config`, `kmwan_set_interface`, `kmwan_set_sensitivity` | [KMWAN](kmwan.md) |
| `mwan3_get_config`, `mwan3_get_status`, `mwan3_set_config`, `mwan3_set_interface` | [MWAN3](mwan3.md) |
| `parental_control_set_temporary_override`, `parental_control_set_filtering_mode`, `parental_control_update_signatures`, `parental_control_set_group_schedules` | [Parental Control](parental-control-feature.md) |
| `access_control_set_mode`, `access_control_set_device_block` | [Access Control](access-control.md) |
| `playground` | [API Playground](playground.md) |

## Core Services

These services are always available regardless of optional feature selection.

| Service | Page |
| --- | --- |
| `set_fan_temperature` | [Smart Fan](smart-fan.md) |
| `refresh_clients` | [Refresh Clients](refresh-clients.md) |

## Reference

- [Targeting a Specific Router](router-targeting.md) — The optional `mac` parameter shared by every service.
- [Triggers](triggers.md) — Building automations that react to GL.iNet router state.
- [Conditions](conditions.md) — Using Home Assistant's built-in conditions on integration entities.
