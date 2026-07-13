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
- `edgerouter`: per-interface WAN status (`get_kmwan_status`) used to build per-interface WAN status sensors.
- `clients`: client list (`get_online`).
- `wifi`: interface config and enable/disable.
- `kmwan`: GL.iNet KMWAN config, interface status, and sensitivity settings.
- `mwan3`: GL.iNet MWAN3 config, interface status, and per-interface detection settings.
- `upgrade`: Firmware update check, online status, and online firmware upgrade calls. The integration uses the firmware release note from `check_firmware_online` to populate Home Assistant's native update entity when available.
- `wg-client` / `vpn-client`: Optional WireGuard client support across older and newer firmware.
- `ovpn-client` / `vpn-client`: Hybrid OpenVPN client support. Discovers profiles via `ovpn-client` and manages state via the unified `vpn-client` tunnel API.
- `wg-server`: Optional WireGuard server status and control.
- `ovpn-server`: Optional OpenVPN server status and control.
- `tailscale`: Tailscale config and state.
- `modem`: optional cellular status.
- `repeater`: optional repeater mode status, configuration, WiFi scan, connect/disconnect, and saved AP management.
- `sms`: optional text message list, send, and delete.
- `zerotier`: ZeroTier config and state.
- `adguardhome`: AdGuard Home config and state.
- `firewall`: Firewall rules, port forwarding, and DMZ management.
- `mcu`: Optional battery warning config and OLED screen display config. Battery live status is reported by `system/get_status` under `mcu`.
- `parental-control`: Parental control config, status, group updates, filtering mode, brief/temporary overrides, and signature updates.
- `black_white_list`: Access control blacklist/whitelist config and single-MAC updates.
- `fan`: Optional fan status, speed, and threshold control.
- `led`: System LED control.
- `macclone`: MAC clone capabilities.

## Firmware Variation

The GL.iNet API surface is not identical across all devices. When adding new features, prefer optional API calls for model-specific modules and expose entities only when useful data is returned.

- Modem status uses `modem/get_info` and `modem/get_status` on firmware 4.8.x. On
  firmware 4.9+ the client uses the newer per-slot modem endpoints and normalizes
  those responses for the existing cellular sensors.

## Repeater Notes

The repeater integration follows the SDK 4.0 repeater module endpoints:

- `repeater/scan` uses the documented `refresh` parameter for forced scans.
- `repeater/connect` supports secured networks by passing `key` only when an action password is provided. The default action path uses DHCP client mode with `manual: false`, `protocol: dhcp`, `disguise: false`, and `auto_portal: false`.
- Saved-network action responses intentionally omit saved WiFi passwords even though the router can return them.

## Error Handling

The integration treats documented/core APIs and optional model-specific APIs differently.

Core APIs:

- Authentication errors raise Home Assistant auth failures.
- Setup connection failures raise Home Assistant setup retry errors.
- Polling timeouts and router error payloads are logged and leave the previous state in place until the router responds again.

Optional APIs:

- LED, cellular, SMS, AdGuard Home, firewall, MCU, parental/access control, and client cache clear calls are optional.
- Unsupported optional APIs are logged at debug level and do not fail setup.
- Entities for optional features are created only when useful data is available or the feature is enabled in options.
