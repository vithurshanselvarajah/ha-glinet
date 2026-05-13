# ha-glinet

Unified GL.iNet support for Home Assistant.

This project is inspired by [HarvsG/ha-glinet4-integration](https://github.com/HarvsG/ha-glinet4-integration), a completely rebuilt Home Assistant custom component for GL.iNet routers running 4.x firmware. This repository keeps that idea moving as a bundled integration plus router API client, with automated tests, docs and a significantly expanded feature set

## What It Does

`ha-glinet` connects Home Assistant to a GL.iNet router over the local network using the router JSON-RPC API at `/rpc`.

Included features:

- Config flow setup with DHCP discovery.
- Robust session management with proactive token renewal and automatic retries.
- Router reboot button.
- Connected device trackers.
- WAN IP address sensor.
- Connected client count sensor.
- Per-client real-time bandwidth (upload/download) and IP address sensors.
- System sensors for CPU temperature, load, memory, flash use, and uptime.
- WiFi interface switches.
- System LED switch.
- WireGuard client and server support.
- OpenVPN client and server support (with location selection).
- Tailscale switch.
- ZeroTier switch (Requires Network ID setup on router).
- AdGuard Home switches (Optional).
- Optional cellular signal/network sensors.
- Optional SMS services for sending, viewing and managing text messages in the inbox.
- Optional repeater mode support for WiFi scan, connect/disconnect, saved networks, and repeater state.
- Fan support (status, RPM, and temperature threshold control).
- Firewall management (DMZ, port forwarding, rules, and WAN access control).
- Automatic cleanup of stale discovered devices.
- **Downloadable Diagnostics**: Provides a sanitized JSON snapshot for easier troubleshooting.


During integration setup you can choose which optional GL.iNet features to enable, including WireGuard, cellular, repeater, SMS, Tailscale, ZeroTier, and Firewall. Unsupported choices are skipped gracefully.

If no optional features are selected, the integration still exposes basic router sensors and device trackers; only optional modules are disabled.

## Why rebuild it? 

Simply put, I use this integration in my own home and wanted specific features that might not align with everyone else's needs. By creating my own version, I can maintain the project freely and implement modifications as I see fit, rather than depending on external reviews and maintenance schedules. 

## Installation

### via HACS (Custom Repository)

1. Open **HACS** in your Home Assistant instance.
2. Click the three dots in the upper right corner and select **Custom repositories**.
3. Enter `https://github.com/vithurshanselvarajah/ha-glinet` in the Repository field.
4. Select **Integration** as the category and click **Add**.
5. Once the repository is added, search for **GL-INet** in the HACS Integrations list.
6. Click **Download** and restart Home Assistant once the download is complete.

### Direct (Manual) Installation

1. Download the latest source code or release ZIP file from this repository.
2. Extract the `custom_components/ha_glinet` directory.
3. Copy the `ha_glinet` folder into your Home Assistant's `config/custom_components/` directory.
4. Restart Home Assistant.

## Setup

1. In Home Assistant, go to **Settings > Devices & services**.
2. Click **Add Integration** in the bottom right.
3. Search for **GL-INet** and select it.
4. Enter your router's URL (default: `http://192.168.8.1`) and admin password.
5. Configure setup options like **Consider Home**, **Update Interval**, and **Enabled Features**. 
6. Choose the optional GL.iNet features you want enabled for this router.
*Note: You can use an HTTPS URL if your router is configured for it and Home Assistant can verify the certificate.*

## Project Layout

- `custom_components/ha_glinet/api`: bundled GL.iNet API client code.
- `custom_components/ha_glinet/entities`: Home Assistant entity implementations.
- `custom_components/ha_glinet`: integration bootstrap, config flow, hub, services, and shared models.
- `docs`: architecture, feature, API, service, and release documentation.
- `tests`: unit tests with mocked API/session behavior.

## Documentation

Detailed documentation lives in [Wiki](https://github.com/vithurshanselvarajah/ha-glinet/wiki).

Start with:

- [Entity Reference](https://github.com/vithurshanselvarajah/ha-glinet/wiki/entities)
- [Services](https://github.com/vithurshanselvarajah/ha-glinet/wiki/services)
- [Router API Notes](https://github.com/vithurshanselvarajah/ha-glinet/wiki/router-api)
- [Developer Reference](https://github.com/vithurshanselvarajah/ha-glinet/wiki/developer-reference)
- [CI and Release Workflows](https://github.com/vithurshanselvarajah/ha-glinet/wiki/ci-release)

## Development Checks

Run:

```powershell
py -m pytest -q
ruff check custom_components tests
py -m compileall -q custom_components tests
```

CI runs those checks automatically for pushes and pull requests.

## Support

If you are using this project, please consider leaving a **star** ⭐. It helps me gauge interest in the project and decide how much of my own resources I should allocate to its continued development.

For support, questions, or community discussion, join our Discord channel:

[![Discord](https://img.shields.io/badge/Discord-7289DA?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/Metvr5hC3m)

## Ownership

Maintained by Vithurshan Selvarajah.

## Special Thanks 

HarvsG for his original project to act as inspiration & GL-INet for both their amazing hardware and API documentation
