# Architecture

`ha-glinet` is a Home Assistant custom integration for GL.iNet routers. It uses local polling against the router JSON-RPC endpoint and does not depend on a cloud service.

## Main Modules

- `custom_components/ha_glinet/api`: bundled async API client for `/rpc`.
- `custom_components/ha_glinet/api/models.py`: strongly-typed dataclasses for API responses.
- `custom_components/ha_glinet/config_flow.py`: Home Assistant setup and options flow.
- `custom_components/ha_glinet/hub.py`: runtime state holder and poller.
- `custom_components/ha_glinet/entities`: entity implementations.
- `custom_components/ha_glinet/models.py`: local data models shared by the hub and entities.
- `custom_components/ha_glinet/services.py`: Service registration and handlers.
- `custom_components/ha_glinet/diagnostics.py`: handles generation of sanitized diagnostic snapshot data.

## Runtime Flow

1. The config flow validates the router URL and password.
2. `GLinetHub` authenticates and stores router metadata.
3. The hub sequentially fetches system, internet, client, WiFi, WireGuard, OpenVPN, Tailscale, ZeroTier, AdGuard Home, cellular, and SMS state. Using a sequential loop instead of concurrent task execution acts as a native rate-limiter, ensuring the router's lighttpd/nginx server is not overwhelmed with JSON-RPC payloads.
4. Home Assistant entities read their values from the strongly-typed dataclasses in the hub.
5. Mutating entities and services call the bundled API client, then refresh affected hub state.

## Polling

The integration uses a user-configurable polling interval (defaulting to 30 seconds) managed by a `DataUpdateCoordinator`. This ensures efficient data fetching and automatic entity updates across all platforms without flooding the router.

Optional modules (Cellular, SMS, VPNs, AdGuard Home) are handled defensively. If a router does not support an optional API (e.g., no modem present) or if it is disabled in the options flow, the coordinator logs a debug message and skips that data point, ensuring the core integration remains functional.
