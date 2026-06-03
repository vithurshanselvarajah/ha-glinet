# Entity Reference (`entities/`)

This page documents the **core** entities exposed by the GL.iNet integration. Core entities are always registered regardless of your optional feature selection.

For entities related to optional features, visit their respective pages:

| Optional Feature | Wiki Page |
| --- | --- |
| Cellular sensors | [Cellular](https://github.com/vithurshanselvarajah/ha-glinet/wiki/cellular) |
| Repeater sensors, switches & selects | [Repeater](https://github.com/vithurshanselvarajah/ha-glinet/wiki/repeater) |
| SMS sensor | [SMS](https://github.com/vithurshanselvarajah/ha-glinet/wiki/sms) |
| Tailscale switch | [Tailscale](https://github.com/vithurshanselvarajah/ha-glinet/wiki/tailscale) |
| WireGuard client switches | [WireGuard Client](https://github.com/vithurshanselvarajah/ha-glinet/wiki/wireguard-client) |
| WireGuard server sensor & switch | [WireGuard Server](https://github.com/vithurshanselvarajah/ha-glinet/wiki/wireguard-server) |
| OpenVPN client switches & location select | [OpenVPN Client](https://github.com/vithurshanselvarajah/ha-glinet/wiki/openvpn-client) |
| OpenVPN server sensor & switch | [OpenVPN Server](https://github.com/vithurshanselvarajah/ha-glinet/wiki/openvpn-server) |
| ZeroTier switch | [ZeroTier](https://github.com/vithurshanselvarajah/ha-glinet/wiki/zerotier) |
| AdGuard Home switches | [AdGuard Home](https://github.com/vithurshanselvarajah/ha-glinet/wiki/adguard-home) |
| Firewall sensors & switches | [Firewall](https://github.com/vithurshanselvarajah/ha-glinet/wiki/firewall) |
| Battery sensors & binary sensor | [MCU Battery](https://github.com/vithurshanselvarajah/ha-glinet/wiki/mcu-battery) |
| Parental control sensors, switches & selects | [Parental & Access Control](https://github.com/vithurshanselvarajah/ha-glinet/wiki/parental-control) |

---

## Buttons

| Entity | Source | Notes |
| --- | --- | --- |
| **Reboot** | `system/reboot` | Reboots the router immediately. |
| **Fan test** | `fan/test_fan` | Diagnostic button to run the fan at full speed for 10 seconds. Available on routers with an active fan. |

---

## Device Trackers

Device trackers are created from online devices returned by the router API **only if the device is already known to Home Assistant** through another integration (e.g., the Mobile App, ESPHome, Zigbee, etc.).

This behavior prevents the integration from automatically adding every guest device, transient client, or unknown IoT device on your network as a new tracker entity.

However, you can enable the **Discover unknown devices** option during integration setup or in the options flow. When enabled, the integration tracks every device seen by the router, regardless of its status in the Home Assistant device registry.

The tracker monitors:

- MAC address
- Name/alias
- IP address while online
- Interface type
- Last activity timestamp

Tracked devices use a `consider_home` logic (default 180s) to prevent entities from flickering to "Away" during brief client sleep cycles or router re-polls. Unhelpful tracker entities can be managed via the standard entity settings in **Settings → Devices & services**.

If a device uses randomized MAC addresses, Home Assistant may see each randomized address as a separate tracker. Disable private/random MAC addressing for that WiFi network when you want stable tracking.

---

## Sensors

### Router Diagnostics

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

### Internet and Traffic

| Entity | Source | Notes |
| --- | --- | --- |
| **WAN status** | `system/get_status` | Current status of the WAN interface (Online, Up, Down). |
| **Connected clients** | `clients/get_list` | Count of currently online tracked clients. |

### Client Bandwidth

Each tracked client includes real-time diagnostic sensors attached to the client device:

- **Download rate** — current download bandwidth.
- **Upload rate** — current upload bandwidth.
- **IP address** — current IP address of the client.

These sensors are created only when the router reports bandwidth fields in the client list. Rates are calculated from delta changes between polls when explicit rate fields are missing.

---

## Switches

| Entity | Source | Notes |
| --- | --- | --- |
| **WiFi interface switches** | `wifi/get_config`, `wifi/set_config` | One switch per WiFi interface reported by the router. |
| **System LED** | `led/get_config`, `led/set_config` | Toggle the system status LED. |

---

## Binary Sensors

| Entity | Source | Notes |
| --- | --- | --- |
| **Fan status** | `fan/get_status` | `True` when the fan is currently running. Available on routers with a fan. |
