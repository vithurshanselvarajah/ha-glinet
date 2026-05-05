# Architecture

`ha-glinet` is a Home Assistant custom integration for GL.iNet routers. It uses local polling against the router JSON-RPC endpoint and does not depend on a cloud service.

## Main Modules

- `custom_components/ha_glinet/api`: bundled async API client for `/rpc`.
- `custom_components/ha_glinet/config_flow.py`: Home Assistant setup and options flow.
- `custom_components/ha_glinet/hub.py`: runtime state holder and poller.
- `custom_components/ha_glinet/entities`: entity implementations.
- `custom_components/ha_glinet/models.py`: local data models shared by the hub and entities.
- `custom_components/ha_glinet/services.py`: Service registration and handlers.

## Runtime Flow

1. The config flow validates the router URL and password.
2. `GLinetHub` authenticates and stores router metadata.
3. The hub fetches system, internet, client, WiFi, WireGuard, Tailscale, cellular, and SMS state concurrently.
4. Home Assistant entities read their values from the hub.
5. Mutating entities and services call the bundled API client, then refresh affected hub state.

## Polling

The integration uses a 30-second polling interval defined by `SCAN_INTERVAL`. 

Optional modules (Cellular, SMS, VPNs) are handled defensively. If a router does not support an optional API (e.g., no modem present), the hub logs a debug message and skips that data point, ensuring the core integration remains functional.
