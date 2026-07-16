# glinet-router Documentation

Welcome to the `glinet-router` documentation. This wiki is meant to help you find the right guide quickly, whether you are setting up the integration for the first time or looking for a specific feature.

## About this Integration

`glinet-router` is a **local polling** Home Assistant integration for **GL.iNet** travel and home routers (such as the Beryl, Slate, Mango, Flint, and similar product lines). It talks directly to the router's built-in JSON-RPC endpoint (`/rpc`) over your local network — no cloud account, no third-party service, and no outbound traffic is required.

The integration provides:

- **Core router telemetry** — system load, memory/flash usage, CPU temperature, uptime, and WAN status for every detected interface.
- **Device tracking & diagnostics** — connected clients with per-client bandwidth and IP address sensors.
- **WiFi and hardware controls** — enable/disable individual SSIDs, toggle the system LED, run a fan test, or reboot the router.
- **Optional modules** — cellular/modem status, repeater site surveys and saved networks, SMS send/receive, WireGuard & OpenVPN client/server toggles, Tailscale, ZeroTier, AdGuard Home, firewall rules & port forwards, KMWAN/MWAN3 multi-WAN policy, parental and access control, MCU battery & OLED configuration, and an API playground.
- **Firmware updates** — a native Home Assistant update entity that pulls release notes from the router.
- **Sanitized diagnostics** — diagnostic downloads with all sensitive data (passwords, tokens, MACs, phone numbers) masked.

All communication happens over your local network using the credentials you provide during setup. If a feature isn't available on your router model, the integration detects that automatically and skips the related calls without breaking the rest of the integration.

---

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant.
2. Search for **GL.iNet Router**.
3. Click **Download**, then restart Home Assistant when the install finishes.

### Manual

1. Download the latest source code or release ZIP from the repository.
2. Extract the `custom_components/glinet_router` directory.
3. Copy the `glinet_router` folder into Home Assistant's `config/custom_components/` directory.
4. Restart Home Assistant.

### Prerequisites

- A GL.iNet router running a firmware that exposes the local JSON-RPC API at `/rpc` (most recent GL.iNet 3.x and 4.x firmwares).
- The admin password for the router's `root` account (this is the same password used to log in to the GL.iNet admin web UI).
- Network reachability from the Home Assistant host to the router (default address `http://192.168.8.1`).

### Setup

1. In Home Assistant, go to **Settings → Devices & Services**.
2. Click **Add Integration** in the bottom-right corner.
3. Search for **GL.iNet** and select it.
4. Enter your router URL (default: `http://192.168.8.1`) and admin password.
5. Choose your setup options, including whether you want device tracking, the polling update frequency, and any optional features to enable.
6. The integration will test the connection and authenticate before saving the entry.

> The router is auto-discovered via DHCP if its hostname starts with `gl-` and the MAC prefix matches a known GL.iNet OUI (`94:83:C4:*`). In that case, Home Assistant will offer the integration in the **Discovered** section of **Devices & Services**.

---

## Removal

To completely remove the GL.iNet Router integration from Home Assistant:

1. Go to **Settings → Devices & Services**.
2. Find the **GL.iNet Router** integration card and click it.
3. Click the three-dot menu in the top-right corner of the device page and choose **Delete**.
4. Confirm the deletion in the dialog.

When removed, Home Assistant will:

- Unload all platforms (sensors, switches, buttons, device trackers, select, update, binary sensor) created by the integration.
- Remove the integration's config entry from `.storage/core.config_entries`.
- Remove the device and its entities from the entity and device registries.
- Forget the device's MAC address as a unique ID so you can re-add the same router later.

> Removing the integration does **not** change any settings on the router itself — the router will continue running with whatever configuration you have on it. The integration only stops talking to the local JSON-RPC API.

If you installed via HACS, you can additionally remove the custom repository from HACS to keep your store clean. If you installed manually, delete the `custom_components/glinet_router` directory and restart Home Assistant.

---

## For End Users

These pages cover what the integration provides, how to configure it, and how to use it in Home Assistant.

- [Feature Matrix](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/features) - A quick overview of supported features and actions.
- [Entity Reference](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/entities) - Detailed list of sensors, switches, buttons, and trackers.
- [Services & Actions](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/services) - Guide on using Home Assistant services to control your router.
- [Automation Templates](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/automations) - Ready-made automations you can paste into Home Assistant.
- [Smart Fan](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/smart-fan) - Fan status, speed, and temperature threshold controls.
- [Unknown Device Management](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/unknown-devices) - Discovery, cleanup, and allow/blocklist handling for unknown devices.
- [SSL Verification](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/ssl-verification) - Manage TLS certificate validation for self-signed router certificates.
- [Refresh Clients](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/refresh-clients) - Force a client list refresh outside the normal polling cycle.
- [Targeting a Specific Router](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/router-targeting) - Use the optional `mac` parameter to address a single router.
- [Triggers](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/triggers) - Building automations that react to GL.iNet router state.
- [Conditions](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/conditions) - Using Home Assistant's built-in conditions on integration entities.

### Core Entity Pages

- [Buttons](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/buttons) - Reboot and fan test buttons.
- [Firmware Update](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/update-entity) - Native Home Assistant firmware update entity.
- [Device Trackers](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/device-trackers) - Per-client device tracking.
- [System Sensors](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/system-sensors) - CPU, load, memory, flash, WAN status, and client bandwidth sensors.
- [Core Switches](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/core-switches) - WiFi interface and system LED switches.
- [Core Binary Sensors](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/core-binary-sensors) - Fan status and other core binary sensors.

### Optional Features

These pages cover configuration, entities, and services for optional modules that can be enabled on supported routers:

- [Cellular](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/cellular) - Monitor cellular connection, signals, and modem diagnostics.
- [Repeater](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/repeater) - Connect to and scan for external WiFi networks, manage saved networks.
- [SMS](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/sms) - Send, receive, and delete text messages.
- [Tailscale](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/tailscale) - Enable or disable Tailscale integration.
- [WireGuard Client](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/wireguard-client) - Toggle configured WireGuard client profiles.
- [WireGuard Server](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/wireguard-server) - Manage the built-in WireGuard server.
- [OpenVPN Client](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/openvpn-client) - Manage and select OpenVPN client configurations.
- [OpenVPN Server](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/openvpn-server) - Manage the built-in OpenVPN server.
- [ZeroTier](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/zerotier) - Enable or disable ZeroTier VPN connections.
- [AdGuard Home](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/adguard-home) - Enable/disable AdGuard Home and DNS redirection.
- [Firewall](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/firewall) - Manage firewall rules, port forwarding, and DMZ settings.
  - [Firewall Rules](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/firewall-rules) - Add and remove custom firewall rules.
  - [Port Forwards](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/port-forwards) - Add and remove port forwarding rules.
  - [DMZ](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/dmz) - Toggle the DMZ and configure the target IP.
  - [WAN Access](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/wan-access) - Toggle WAN ping, HTTPS, and SSH remote access.
- [MCU Battery](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/mcu-battery) - Monitor battery status and configure high/low temperature warnings.
- [MCU OLED](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/mcu-oled) - Configure what is displayed on the router's OLED screen.
- [Parental & Access Control](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/parental-control) - Manage internet access blocks and parental group rules per client.
  - [Parental Control](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/parental-control-feature) - Group switches, filtering mode, overrides, and signature updates.
  - [Access Control](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/access-control) - Per-client internet access switches and blacklist/whitelist controls.
- [KMWAN](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/kmwan) - Read and update GL.iNet's KMWAN multi-WAN configuration.
- [MWAN3](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/mwan3) - Read and update MWAN3 multi-WAN configuration.
- [API Playground](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/playground) - Send custom JSON-RPC or ubus commands and inspect the response.

## For Developers

These pages are aimed at the architecture, API details, and maintenance work behind the integration.

- [Developer Reference](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/developer-reference) - Start here for contribution notes, tooling, and project structure.
- [Architecture](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/architecture) - How the integration is structured and interacts with Home Assistant.
- [Runtime State & Poller (Hub)](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/hub) - Details on the `GLinetHub` and `DataUpdateCoordinator`.
  - [Hub Core Functions](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/hub-core) - Coordinator lifecycle and API helpers.
  - [Data Fetching](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/hub-data-fetching) - Per-feature polling methods.
  - [Action Functions](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/hub-action-functions) - Hub write methods.
  - [Option Updates](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/hub-option-updates) - Runtime application of configuration option changes.
  - [Parental Control Helpers](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/hub-parental-helpers) - Group lookup and access control helpers.
- [Router API Notes](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/router-api) - Notes on the GL.iNet JSON-RPC API and authentication.
- [Modem API Coverage](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/modem-api) - Details on the optional cellular modem API.
- [CI and Release Workflows](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/ci-release) - How automated testing and releases work.
