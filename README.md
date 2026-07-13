# ha-glinet

Unified GL.iNet support for Home Assistant.

[![GitHub Release](https://img.shields.io/github/v/release/vithurshanselvarajah/ha-glinet?style=flat-square)](https://github.com/vithurshanselvarajah/ha-glinet/releases)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg?style=flat-square)](https://github.com/hacs/integration)
[![License](https://img.shields.io/github/license/vithurshanselvarajah/ha-glinet?style=flat-square)](LICENSE)
[![Discord](https://img.shields.io/badge/Discord-7289DA?style=flat-square&logo=discord&logoColor=white)](https://discord.gg/Metvr5hC3m)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

This project is a custom Home Assistant integration for GL.iNet routers running 4.x firmware. It includes a full API client, automated tests, detailed documentation, and an expanded set of features.

---

## Quick Links
- [User Documentation & Feature Details](https://github.com/vithurshanselvarajah/ha-glinet/wiki)
- [Installation Guide](#installation)
- [Setup & Configuration](#setup)
- [Join our Discord](https://discord.gg/Metvr5hC3m)

---

## Features
The integration connects to your router over the local network using the GL.iNet JSON-RPC API. Here is a breakdown of what it can do:

### Router Control & Diagnostics
* **Easy Setup**: Supports config flow and automatically finds your router via DHCP.
* **Reliable Connection**: Keeps your login session alive automatically and retries if the connection drops.
* **Toggles**: Control the router's system LED, reboot it, or turn individual WiFi bands on and off.
* **Diagnostics**: Monitors CPU temperature, system load, memory, flash usage, uptime, and lets you download a sanitized diagnostic snapshot.
- **Firmware Updates**: Exposes the router firmware through Home Assistant's native update entity, including a model-specific GL.iNet stable release URL for release notes.

### Connected Devices & Traffic
* **Presence Tracking**: Tracks connected clients as Home Assistant device trackers (and automatically cleans up stale entries).
* **Traffic Stats**: Monitors the total client count and tracks real-time upload/download speeds and IP addresses per client.
* **WAN Info**: Keeps track of the external WAN IP address.

### VPN & Ad-Blocking Toggles
* **Standard VPNs**: Easily toggle WireGuard and OpenVPN clients/servers (including choosing locations for OpenVPN).
* **Mesh Networks**: Toggles Tailscale and ZeroTier (requires network ID setup on the router).
* **AdGuard**: Turn the built-in AdGuard Home instance on and off.

### Cellular, SMS & Hardware Controls
* **Cellular Support**: Optional sensors for cellular signal strength and network status.
* **SMS Gateway**: Read, send, and manage text messages from your router's SIM card in Home Assistant.
* **Repeater Mode**: Scan for nearby WiFi networks, connect (open or secured), disconnect, save networks, and track the current repeater status.
* **Smart Fan**: Monitor fan status, speed (RPM), and set temperature thresholds.
* **Firewall Controls**: Manage DMZ, port forwarding, custom rules, and WAN access.
* **WAN Policy**: Optional KMWAN and MWAN3 actions for reading and updating multi-WAN configuration without adding cluttered entities.

During setup, you can select which optional features (like VPN, Cellular, Repeater, SMS, and Firewall) to enable. Unsupported features on your router model will be skipped gracefully.

---

## Installation

### Using HACS (Recommended)
1. Open **HACS** in your Home Assistant instance.
2. Go to **Integrations** and search for **GL‑INet**.
3. Click **Download**, then restart Home Assistant once complete.

### Manual Installation
1. Download the latest source code or release ZIP.
2. Extract the `custom_components/ha_glinet` directory.
3. Copy the `ha_glinet` folder into your Home Assistant's `config/custom_components/` directory.
4. Restart Home Assistant.

---

## Setup

1. In Home Assistant, navigate to **Settings > Devices & services**.
2. Click **Add Integration** in the bottom-right corner.
3. Search for **GL-INet** and select it.
4. Enter your router's URL (default: `http://192.168.8.1`) and admin password.
5. Select setup options like **Consider Home** (for trackers), **Update Interval**, and select which optional features to enable, including WAN policy controls if you want them.

---

## Wiki & Documentation

Detailed documentation lives in the project [Wiki](https://github.com/vithurshanselvarajah/ha-glinet/wiki).

### For End Users
* [Feature Matrix](https://github.com/vithurshanselvarajah/ha-glinet/wiki/features) — What features are supported on each model.
* [Entity Reference](https://github.com/vithurshanselvarajah/ha-glinet/wiki/entities) — A list of all sensors, switches, and trackers created by the integration.
* [Services & Actions](https://github.com/vithurshanselvarajah/ha-glinet/wiki/services) — How to call services to control the router (e.g. sending SMS or connecting to repeater WiFi).
* [Automation Templates](https://github.com/vithurshanselvarajah/ha-glinet/wiki/automations) — Ready-made automations you can import (SMS notifications, etc.).

### For Developers
* [Developer Reference](https://github.com/vithurshanselvarajah/ha-glinet/wiki/developer-reference) — Code style, structure, and development tools.
* [Architecture](https://github.com/vithurshanselvarajah/ha-glinet/wiki/architecture) — How components and update poller work together.
* [Runtime Hub](https://github.com/vithurshanselvarajah/ha-glinet/wiki/hub) — Details about state polling and coordinators.
* [Router API Details](https://github.com/vithurshanselvarajah/ha-glinet/wiki/router-api) — Notes on GL.iNet RPC calls.
* [Modem API](https://github.com/vithurshanselvarajah/ha-glinet/wiki/modem-api) — Cellular modem API structure.
* [CI & Releases](https://github.com/vithurshanselvarajah/ha-glinet/wiki/ci-release) — Testing and release workflows.

<details>
<summary><b>Developer Quick Start</b> (Click to expand)</summary>

### Project Layout
* `custom_components/ha_glinet/api`: Bundled GL.iNet API client code.
* `custom_components/ha_glinet/entities`: Home Assistant entity implementations.
* `custom_components/ha_glinet`: Integration bootstrap, config flow, hub, services, and shared models.
* `docs`: Raw markdown files for the documentation wiki.
* `ha-automations`: Home Assistant automation templates ready to import.
* `tests`: Unit tests with mocked API/session behavior.

### Development Checks
Run the following commands locally to verify code style and tests:
```powershell
py -m pytest -q
ruff check custom_components tests
py -m compileall -q custom_components tests
```
</details>

---

## Support & Contribution

If you find this project useful, please consider leaving a star. It helps gauge interest and prioritize development!

For support, questions, or community discussion, join our Discord:

[![Discord Banner](https://img.shields.io/badge/Discord-7289DA?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/Metvr5hC3m)

### Why Rebuild?
Simply put, I use this integration in my own home and wanted specific features that might not align with everyone else's needs. Maintaining my own integration allows me to iterate quickly and tailor the features.

### Special Thanks
* **HarvsG** for the original [ha-glinet4-integration](https://github.com/HarvsG/ha-glinet4-integration) project which inspired this version.
* **GL.iNet** for their amazing hardware and detailed API documentation.
