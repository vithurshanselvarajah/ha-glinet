# Services & Actions (`services.py`)

The integration registers services under the `ha_glinet` domain to allow manual interaction with the router from Home Assistant automations and scripts.

Services are registered dynamically based on your **Enabled Features** configuration. If a feature (e.g., SMS) is disabled across all configured routers, its services are automatically removed from Home Assistant to keep the UI clean.

For full parameter details, visit the optional feature page for each service group:

| Service Group | Feature Page |
| --- | --- |
| `send_sms`, `get_sms`, `remove_sms`, `refresh_sms` | [SMS](https://github.com/vithurshanselvarajah/ha-glinet/wiki/sms) |
| `scan_wifi`, `connect_wifi`, `disconnect_wifi`, `get_saved_networks`, `remove_saved_network` | [Repeater](https://github.com/vithurshanselvarajah/ha-glinet/wiki/repeater) |
| `add_firewall_rule`, `remove_firewall_rule`, `get_firewall_rules`, `add_port_forward`, `remove_port_forward`, `set_dmz` | [Firewall](https://github.com/vithurshanselvarajah/ha-glinet/wiki/firewall) |
| `get_mcu_battery_config`, `set_mcu_battery_config` | [MCU Battery](https://github.com/vithurshanselvarajah/ha-glinet/wiki/mcu-battery) |
| `get_mcu_oled_config`, `set_mcu_oled_config` | [MCU OLED](https://github.com/vithurshanselvarajah/ha-glinet/wiki/mcu-oled) |
| `kmwan_get_config`, `kmwan_get_status`, `kmwan_set_config`, `kmwan_set_interface`, `kmwan_set_sensitivity` | [KMWAN](https://github.com/vithurshanselvarajah/ha-glinet/wiki/router-api) |
| `mwan3_get_config`, `mwan3_get_status`, `mwan3_set_config`, `mwan3_set_interface` | [MWAN3](https://github.com/vithurshanselvarajah/ha-glinet/wiki/router-api) |
| `parental_control_set_temporary_override`, `parental_control_set_filtering_mode`, `parental_control_update_signatures`, `access_control_set_mode`, `access_control_set_device_block`, `parental_control_set_group_schedules` | [Parental & Access Control](https://github.com/vithurshanselvarajah/ha-glinet/wiki/parental-control) |
| `playground` | [API Playground](https://github.com/vithurshanselvarajah/ha-glinet/wiki/playground) |

---

## API Playground

### `playground`

Sends a custom JSON-RPC or ubus request to the GL-INet router and waits to return the raw JSON response. This service is only available if **API Playground** is enabled in the configuration flow options.

For a full guide, request-routing rules, and multiple examples, see the dedicated [API Playground Documentation](playground.md) (or [Wiki page](https://github.com/vithurshanselvarajah/ha-glinet/wiki/playground)).

- **`method`**: The RPC or ubus method. Use a slash to call ubus objects, e.g. `system/get_info`, or specify top-level RPC methods (like `challenge`).
- **`body`** (Optional): A JSON/YAML dictionary containing parameters/arguments for the request.
- **`mac`** (Optional): Target a specific router by MAC address.

---


## Fan Control

### `set_fan_temperature`

Sets the temperature threshold at which the router's fan will start running. Available on routers with a controllable fan.

- **`temperature`**: Target threshold temperature in Celsius (typically 70–90).
- **`mac`** (Optional): Target a specific router by MAC address.

---

## Targeting a Specific Router

All services accept an optional **`mac`** parameter. When multiple GL.iNet routers are configured in Home Assistant, you can use the router's MAC address to target a specific instance. If omitted, the first available hub is used.

---

## Internal Logic

| Function | Purpose |
| --- | --- |
| `async_register_services` | Entry point during integration setup to register all domain services. |
| `_get_hub` | Helper to find the active `GLinetHub` instance matching the provided MAC address. |
