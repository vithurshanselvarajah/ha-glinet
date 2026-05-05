# ha-glinet

Unified GL.iNet support for Home Assistant.

This project is inspired by [HarvsG/ha-glinet4-integration](https://github.com/HarvsG/ha-glinet4-integration), a completely rebuilt Home Assistant custom component for GL.iNet routers running 4.x firmware. This repository keeps that idea moving as a bundled integration plus router API client, with automated tests, docs and a significantly expanded feature set

## What It Does

`ha-glinet` connects Home Assistant to a GL.iNet router over the local network using the router JSON-RPC API at `/rpc`.

Included features:

- Config flow setup with DHCP discovery.
- Router reboot button.
- Connected device trackers.
- WAN IP and internet connectivity sensors.
- Connected client count and bandwidth sensors.
- System sensors for CPU temperature, load, memory, flash use, and uptime.
- WiFi interface switches.
- WireGuard client switches.
- Tailscale switch.
- Optional cellular signal/network sensors.
- Optional SMS services for sending, viewing and managing text messages in the inbox.

GL.iNet firmware varies by router model. Optional APIs such as cellular and SMS are detected defensively and skipped when unsupported.

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

*Note: You can use an HTTPS URL if your router is configured for it and Home Assistant can verify the certificate.*

## Project Layout

- `custom_components/ha_glinet/api`: bundled GL.iNet API client code.
- `custom_components/ha_glinet/entities`: Home Assistant entity implementations.
- `custom_components/ha_glinet`: integration bootstrap, config flow, hub, services, and shared models.
- `docs`: architecture, feature, API, service, and release documentation.
- `tests`: unit tests with mocked API/session behavior.

## Documentation

Detailed documentation lives in [docs](docs/README.md).

Start with:

- [Entity Reference](docs/entities.md)
- [Services](docs/services.md)
- [Router API Notes](docs/router-api.md)
- [CI and Release Workflows](docs/ci-release.md)

## Development Checks

Run:

```powershell
py -m pytest -q
ruff check custom_components tests
py -m compileall -q custom_components tests
```

CI runs those checks automatically for pushes and pull requests.

## Ownership

Maintained by Vithurshan Selvarajah.

## Special Thanks 

HarvsG for his original project to act as inspiration
GL-INet for both their amazing hardware and API documentation
