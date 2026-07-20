# Core Switches

The integration exposes two core switches that are always available regardless of optional feature selection.

| Entity | Source | Notes |
| --- | --- | --- |
| **WiFi interface switches** | `wifi/get_config`, `wifi/set_config` | One switch per WiFi interface reported by the router. |
| **System LED** | `led/get_config`, `led/set_config` | Toggle the system status LED. |

## Related Pages

- [Entity Reference parent page](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/entities)
- [System Sensors](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/system-sensors) — CPU, load, memory, flash, and WAN status sensors.
- [Binary Sensors](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/core-binary-sensors) — Fan status, repeater, and parental override sensors.
