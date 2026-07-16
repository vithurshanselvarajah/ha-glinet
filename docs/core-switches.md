# Core Switches

The integration exposes two core switches that are always available regardless of optional feature selection.

| Entity | Source | Notes |
| --- | --- | --- |
| **WiFi interface switches** | `wifi/get_config`, `wifi/set_config` | One switch per WiFi interface reported by the router. |
| **System LED** | `led/get_config`, `led/set_config` | Toggle the system status LED. |

## Related Pages

- [Entity Reference parent page](entities.md)
- [System Sensors](system-sensors.md) — CPU, load, memory, flash, and WAN status sensors.
- [Binary Sensors](core-binary-sensors.md) — Fan status, repeater, and parental override sensors.
