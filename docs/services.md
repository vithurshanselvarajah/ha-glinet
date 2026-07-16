# Services & Actions

The integration registers services under the `glinet_router` domain to allow manual interaction with the router from Home Assistant automations and scripts.

Services are registered dynamically based on your **Enabled Features** configuration. If a feature (e.g., SMS) is disabled across all configured routers, its services are automatically removed from Home Assistant to keep the UI clean.

For full parameter details, visit the optional feature page for each service group:

| Service Group | Feature Page |
| --- | --- |
| `send_sms`, `get_sms`, `remove_sms`, `refresh_sms` | [SMS](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/sms) |
| `scan_wifi`, `connect_wifi`, `disconnect_wifi`, `get_saved_networks`, `remove_saved_network` | [Repeater](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/repeater) |
| `add_firewall_rule`, `remove_firewall_rule`, `get_firewall_rules` | [Firewall Rules](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/firewall-rules) |
| `add_port_forward`, `remove_port_forward` | [Port Forwards](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/port-forwards) |
| `set_dmz` | [DMZ](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/dmz) |
| `get_mcu_battery_config`, `set_mcu_battery_config` | [MCU Battery](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/mcu-battery) |
| `get_mcu_oled_config`, `set_mcu_oled_config` | [MCU OLED](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/mcu-oled) |
| `kmwan_get_config`, `kmwan_get_status`, `kmwan_set_config`, `kmwan_set_interface`, `kmwan_set_sensitivity` | [KMWAN](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/kmwan) |
| `mwan3_get_config`, `mwan3_get_status`, `mwan3_set_config`, `mwan3_set_interface` | [MWAN3](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/mwan3) |
| `parental_control_set_temporary_override`, `parental_control_set_filtering_mode`, `parental_control_update_signatures`, `parental_control_set_group_schedules` | [Parental Control](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/parental-control-feature) |
| `access_control_set_mode`, `access_control_set_device_block` | [Access Control](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/access-control) |
| `playground` | [API Playground](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/playground) |

## Core Services

These services are always available regardless of optional feature selection.

| Service | Page |
| --- | --- |
| `set_fan_temperature` | [Smart Fan](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/smart-fan) |
| `refresh_clients` | [Refresh Clients](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/refresh-clients) |

## Reference

- [Targeting a Specific Router](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/router-targeting) — The optional `mac` parameter shared by every service.
- [Triggers](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/triggers) — Building automations that react to GL.iNet router state.
- [Conditions](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/conditions) — Using Home Assistant's built-in conditions on integration entities.
