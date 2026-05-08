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
- `send_sms`, `get_sms`, `remove_saved_network`, and `refresh_sms` services.
- Repeater mode scanning, connect/disconnect, saved network management, and repeater state support.
- Fan status monitoring, RPM speed, and threshold temperature control.

## Supported Actions

- Reboot router.
- Enable or disable WiFi interfaces.
- Enable or disable WireGuard client profiles.
- Enable or disable Tailscale when configured.
- Send text messages when the router exposes SMS support.
- Remove text messages when the router exposes SMS support.
- Trigger a 10-second fan test.
- Set the fan threshold temperature.

## Authentication & Session Management

To ensure reliable communication and minimize session expiration issues:
- **Proactive Refresh**: The integration refreshes the session token at the beginning of every polling cycle.
- **Retry Mechanism**: Token renewal attempts are retried up to 3 times if the router returns an authentication or token error.
- **Detailed Logging**: If renewal fails, the integration logs the specific error response or exception received from the router for easier troubleshooting.
- **Graceful Failure**: If all retries fail, a re-authentication flow is triggered in Home Assistant to prompt the user for credentials.

## Setup Configuration Options

When adding the GL.iNet integration or modifying it via the **Configure** menu, the following options are available:

- **Router URL**: The network address of your router (e.g., `http://192.168.8.1`). HTTPS is supported if configured on the router.
- **Admin Password**: The password for the `root` account used to access the GL.iNet admin panel.
- **Consider Home**: Defines the grace period (in seconds) before a device is marked as "Away" in Home Assistant. This helps prevent devices from flickering when they briefly drop off the network.
- **Enabled Features**: A selection of optional modules to activate for this router instance:
    - **Cellular**: Enables signal and network monitoring for routers with internal or USB modems.
    - **Repeater**: Enables WiFi station mode management, scanning, and saved network control.
    - **SMS**: Enables the text message inbox sensor and SMS sending/management actions.
    - **Tailscale / WireGuard**: Enables monitoring and toggling of VPN connections.

## Optional Router Support

GL.iNet firmware varies by model and firmware generation. The integration treats WireGuard, cellular, repeater, SMS, and Tailscale as optional modules. During setup you can choose which of these optional features to enable, and unsupported or unavailable APIs are skipped without failing setup.

If you disable all optional features, the integration still registers core router status sensors and entities. 

### Dynamic Configuration & Cleanup

The integration dynamically manages its footprint based on your selections in the **Configure** menu:
- **Entity Cleanup**: When a feature is disabled, the integration automatically removes any associated entities from the Home Assistant Entity Registry.
- **Action Cleanup**: Services (Actions) are registered at the domain level. If a feature (like SMS) is disabled across all configured routers, the corresponding services are automatically removed from Home Assistant to keep the UI clean.
