# Core Binary Sensors

The integration exposes core binary sensors. Some are always available, while others depend on optional features.

## Always Available

| Entity | Source | Notes |
| --- | --- | --- |
| **Fan status** | `fan/get_status` | `True` when the fan is currently running. Available on routers with a fan. |

## Feature-Gated

| Entity | Source | Notes |
| --- | --- | --- |
| **Repeater connected** | `repeater/get_status` | `True` when the repeater is connected or WAN is available. Available when the Repeater feature is enabled. Attributes include SSID, BSSID, signal, WiFi generation, EAP, and bare mode. |
| **Repeater bare mode** | `repeater/get_status` | Diagnostic sensor. `True` when repeater bare mode is active. Available when the Repeater feature is enabled. |
| **Parental control group override** | `parental-control/get_status` | One diagnostic binary sensor per parental group. `True` when a temporary override is currently active for that group. Available when the Parental & Access Control feature is enabled. |

## Related Pages

- [Entity Reference parent page](entities.md)
- [System Sensors](system-sensors.md) — CPU, load, memory, flash, and WAN status sensors.
- [Core Switches](core-switches.md) — WiFi and LED core switches.
