# System Sensors (Core)

The integration exposes system status sensors that are always available regardless of optional feature selection.

## Router Diagnostics

| Entity | Source | Notes |
| --- | --- | --- |
| **CPU temperature** | `system/get_status` | Diagnostic sensor. Available when supported by the router. |
| **Load avg (1m)** | `system/get_status` | Diagnostic sensor. |
| **Load avg (5m)** | `system/get_status` | Diagnostic sensor. |
| **Load avg (15m)** | `system/get_status` | Diagnostic sensor. |
| **Memory usage** | `system/get_status` | Calculated from total/free memory. |
| **Flash usage** | `system/get_status` | Calculated from total/free flash. |
| **Uptime** | `system/get_status` | Timestamp sensor. |
| **Fan speed** | `fan/get_status` | Diagnostic sensor showing current fan RPM. Available on routers with a fan. |
| **Fan threshold temperature** | `fan/get_config` | Diagnostic sensor showing the current fan temperature threshold. Available on routers with a fan. |

## Internet and Traffic

| Entity | Source | Notes |
| --- | --- | --- |
| **WAN status (per interface)** | `edgerouter/get_status` | One sensor per detected WAN interface (e.g., Ethernet 1, Ethernet 2, Repeater, Cellular, Tethering). Reports `Up`, `Down`, or `Unknown`. Specific interfaces and protocols (IPv4/IPv6) can be configured via the **WAN Status Monitors** option in the options flow. |
| **Connected clients** | `clients/get_online` | Count of currently online tracked clients. |

## Client Bandwidth

Each tracked client includes real-time diagnostic sensors attached to the client device:

- **Download rate** — current download bandwidth.
- **Upload rate** — current upload bandwidth.
- **IP address** — current IP address of the client.

These sensors are created only when the router reports bandwidth fields in the client list. Rates are calculated from delta changes between polls when explicit rate fields are missing.

## Related Pages

- [Entity Reference parent page](entities.md)
- [Switches](core-switches.md) — WiFi and LED core switches.
- [Binary Sensors](core-binary-sensors.md) — Fan status, repeater, and parental override sensors.
