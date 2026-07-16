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

## Related Pages

- [KMWAN](kmwan.md) — KMWAN multi-WAN services.
- [MWAN3](mwan3.md) — MWAN3 multi-WAN services.
- [Modem API Coverage](modem-api.md) — Cellular modem API.
