# Feature Matrix & Supported Actions

## Existing Core Features

- Config flow setup with DHCP discovery.
- Router device metadata.
- Reboot button.
- Connected device trackers.
- CPU temperature, load average, memory usage, flash usage, and uptime sensors.
- WiFi interface switches.
- WireGuard client switches.
- Tailscale switch.

## Added Operational Features

- Connected clients count sensor from online tracked clients.
- Per-client bandwidth rate sensors attached to client MAC devices.
- Cellular signal and network sensors using the optional `modem` module.
- Text message count sensor with message details as attributes.
- `send_sms`, `get_sms`, `remove_sms`, and `refresh_sms` services.

## Supported Actions

- Reboot router.
- Enable or disable WiFi interfaces.
- Enable or disable WireGuard client profiles.
- Enable or disable Tailscale when configured.
- Send text messages when the router exposes SMS support.
- Remove text messages when the router exposes SMS support.

## Optional Router Support

GL.iNet firmware varies by model and firmware generation. The integration treats cellular and SMS as optional modules. Unsupported API calls are skipped without failing setup.
