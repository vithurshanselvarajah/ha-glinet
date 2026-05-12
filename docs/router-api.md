# Router API Notes

The bundled API client follows the GL.iNet firmware API guide in `dev-docs.docx`.

## Endpoint

All requests are posted to:

```text
http://<router-address>/rpc
```

## Authentication

The router uses JSON-RPC challenge-response authentication.

1. Call `challenge` with username `root`.
2. Read `alg`, `salt`, and `nonce`.
3. Generate a Unix-style password hash using the algorithm requested by `alg`.
4. Hash `username:cipherPassword:nonce`.
5. Call `login` with the generated hash.
6. Store the returned `sid`.

Authenticated calls use JSON-RPC method `call` and pass:

```text
sid, module-name, function-name, optional parameters
```

## Implemented Modules

- `system`: router info, status, reboot.
- `edgerouter`: internet/WAN status.
- `clients`: client list and optional cache clear.
- `wifi`: interface config and enable/disable.
- `wg-client` / `vpn-client`: Optional WireGuard client support across older and newer firmware.
- `ovpn-client` / `vpn-client`: Hybrid OpenVPN client support. Discovers profiles via `ovpn-client` and manages state via the unified `vpn-client` tunnel API.
- `wg-server`: Optional WireGuard server status and control.
- `tailscale`: Tailscale config and state.
- `modem`: optional cellular status.
- `repeater`: optional repeater mode status, configuration, WiFi scan, connect/disconnect, and saved AP management.
- `sms`: optional text message list, send, and delete.
- `zerotier`: ZeroTier config and state.
- `adguardhome`: AdGuard Home config and state.
- `led`: System LED control.

## Firmware Variation

The GL.iNet API surface is not identical across all devices. When adding new features, prefer optional API calls for model-specific modules and expose entities only when useful data is returned.

## Error Handling

The integration treats documented/core APIs and optional model-specific APIs differently.

Core APIs:

- Authentication errors raise Home Assistant auth failures.
- Setup connection failures raise Home Assistant setup retry errors.
- Polling timeouts and router error payloads are logged and leave the previous state in place until the router responds again.

Optional APIs:

- LED, cellular, SMS, AdGuard Home, and client cache clear calls are optional.
- Unsupported optional APIs are logged at debug level and do not fail setup.
- Entities for optional features are created only when useful data is available or the feature is enabled in options.
