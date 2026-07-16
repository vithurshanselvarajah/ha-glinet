# Architecture

`glinet-router` is a Home Assistant custom integration for GL.iNet routers. It uses local polling against the router JSON-RPC endpoint and does not depend on a cloud service.

## Main Modules

- `custom_components/glinet_router/api`: bundled async API client for `/rpc`.
- `custom_components/glinet_router/api/models.py`: strongly-typed dataclasses for API responses.
- `custom_components/glinet_router/config_flow.py`: Home Assistant setup and options flow.
- `custom_components/glinet_router/hub.py`: runtime state holder and poller.
- `custom_components/glinet_router/entities`: entity implementations.
- `custom_components/glinet_router/models.py`: local data models shared by the hub and entities.
- `custom_components/glinet_router/services.py`: Service registration and handlers.
- `custom_components/glinet_router/diagnostics.py`: handles generation of sanitized diagnostic snapshot data.

## Runtime Flow

1. The config flow validates the router URL and password.
2. `GLinetHub` authenticates and stores router metadata.
3. The hub sequentially fetches system status, per-interface WAN status, firmware update metadata, client list, WiFi, fan, LED, WireGuard, OpenVPN, Tailscale, ZeroTier, AdGuard Home, cellular, firewall, parental control, SMS, and repeater state. Using a sequential loop instead of concurrent task execution acts as a native rate-limiter, ensuring the router's lighttpd/nginx server is not overwhelmed with JSON-RPC payloads.
4. Home Assistant entities read their values from the strongly-typed dataclasses in the hub.
5. Mutating entities and services call the bundled API client, then refresh affected hub state.

## Polling

The integration uses a user-configurable polling interval (defaulting to 30 seconds, clamped to the 10–300s range by the config flow) managed by a `DataUpdateCoordinator`. This ensures efficient data fetching and automatic entity updates across all platforms without flooding the router.

Optional modules (Cellular, SMS, VPNs, WAN policy, AdGuard Home) are handled defensively. If a router does not support an optional API (e.g., no modem present) or if it is disabled in the options flow, the coordinator logs a debug message and skips that data point, ensuring the core integration remains functional.

## Config Flow & Setup

- The config flow (`config_flow.py`) is the only supported setup path — `config_flow: true` is set in `manifest.json`.
- During the user step, the flow calls `process_user_input` which:
  1. Sends a reachability check (`is_router_reachable`) to the router.
  2. Performs a full login (`authenticate` + `system.get_info`) to validate the password.
  3. Discovers available WAN interfaces and rebuilds the WAN monitor selector.
- On success, the unique ID is set to the lowercase, colon-separated MAC address via `format_mac` and the entry is rejected with `already_configured` if that MAC is already present. This guarantees a single config entry per physical router.
- DHCP discovery (`async_step_dhcp`) is configured for hostnames starting with `gl-*` and the GL.iNet OUI `94:83:C4*`. Discovery pre-fills the host field and reuses the validation path with `raise_on_invalid_auth=False` so the user is not blocked by a temporary bad password during discovery.

## Runtime Data

Per the `runtime-data` quality scale rule, the hub instance is stored on `ConfigEntry.runtime_data` (not on `hass.data[DOMAIN]`). All entity platforms read it through `entry.runtime_data`, and platform/entity cleanup uses the standard Home Assistant lifecycle (`async_on_unload`, `entry.async_on_unload`).

## Service Registration

Services are registered in `async_setup_entry` (via `services.async_register_services`) rather than during `async_setup`, so each config entry drives the service registration that owns its router. Services are dynamically added or removed as features are enabled/disabled at the option-flow level, and removal is performed on entry unload.

## Related Pages

- [Developer Reference](developer-reference.md) — Contributing, tooling, and project structure.
- [Runtime State & Poller (Hub)](hub.md) — Details on the `GLinetHub` and `DataUpdateCoordinator`.
- [Router API Notes](router-api.md) — Endpoints, authentication, and module inventory.
- [Sensor Cleanup](sensor-cleanup.md) — How the integration keeps the entity registry in sync with the router.
