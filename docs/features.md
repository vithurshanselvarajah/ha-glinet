# Feature Matrix & Supported Actions

## Existing Core Features

- Config flow setup with DHCP discovery.
- Router device metadata.
- Reboot button.
- Connected device trackers.
- CPU temperature, load average, memory usage, flash usage, and uptime sensors.
- WiFi interface switches.
- System LED switch.
- AdGuard Home switches (Optional).
- WireGuard client and server switches.
- OpenVPN client and server switches.
- Tailscale switch.
- ZeroTier switch (Requires Network ID setup on router).
- Firewall management (DMZ, port forwarding, and rules).
- WAN access control (Ping, HTTPS, SSH).
- Parental & Access Control feature group for device internet access and parental profiles.

## Added Operational Features

- Connected clients count sensor from online tracked clients.
- Per-client bandwidth rate and IP address sensors attached to client MAC devices.
- Cellular signal and network sensors using the optional `modem` module.
- Text message count sensor with message details as attributes.
- `send_sms`, `get_sms`, `remove_saved_network`, and `refresh_sms` services.
- Repeater mode scanning, connect/disconnect, saved network management, smart availability, expanded state support, bare mode, and smart reconnect toggles.
- Fan status monitoring, RPM speed, and threshold temperature control.
- WireGuard server connected users count.
- OpenVPN server connected users count.
- AdGuard Home management (Enable/Disable, DNS control).
- Custom firewall rules and port forwarding management.
- Device-level Internet access switches attached to tracked client devices.
- Device-level Parental control group selectors attached to tracked client devices.
- Router-level parental control global, group, and override state entities.
- Automatic stale device registry cleanup.

## Supported Actions

- Reboot router.
- Enable or disable WiFi interfaces.
- Enable or disable the System LED.
- Enable or disable WireGuard client profiles or server.
- Enable or disable OpenVPN client profiles or server.
- Enable or disable Tailscale when configured.
- Send text messages when the router exposes SMS support.
- Remove text messages when the router exposes SMS support.
- Trigger a 10-second fan test.
- Set the fan threshold temperature.
- Add or remove custom firewall rules.
- Add or remove port forwarding rules.
- Enable or disable DMZ.
- Configure WAN-side management access (Ping, HTTPS, SSH).
- Enable or disable internet access for an individual client device.
- Assign an individual client device to a parental control profile group.
- Enable or disable parental control globally or per group.
- Run advanced parental/access actions such as temporary overrides, filtering mode changes, signature updates, and blacklist/whitelist mode changes.
- Connect the router to open or secured external WiFi networks via the `connect_wifi` action.
- Enable or disable repeater bare mode.
- Enable or disable repeater smart reconnect.

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
- **Update Interval**: The polling frequency (in seconds) between 10s and 300s (default 30s). Increase this if you experience router slowdowns.
- **Consider Home**: Defines the grace period (in seconds) before a device is marked as "Away" in Home Assistant. This helps prevent devices from flickering when they briefly drop off the network.
- **Discover unknown devices**: A toggle to choose whether to add *all* newly discovered devices to the Home Assistant device registry or only keep tracked/known devices. Toggling this off will automatically clean up any untracked devices.
- **Auto-cleanup unknown devices (min)**: Defines the period of inactivity (in minutes) after which an unknown discovered device is automatically removed from the registry. Set to 0 to disable automatic cleanup.
- **Enabled Features**: A selection of optional modules to activate for this router instance:
    - **Cellular**: Enables signal and network monitoring for routers with internal or USB modems.
    - **Repeater**: Enables WiFi station mode management, scanning, and saved network control.
    - **SMS**: Enables the text message inbox sensor and SMS sending/management actions.
    - **Tailscale / WireGuard / OpenVPN / ZeroTier**: Enables monitoring and toggling of VPN connections and servers.
    - **Firewall**: Enables firewall/port-forward counters, firewall switches, and firewall rule actions.
    - **MCU Battery**: Enables battery status sensors and MCU battery warning config actions.
    - **MCU OLED**: Enables MCU OLED config actions.
    - **Parental & Access Control**: Enables per-client internet access switches, per-client parental group selectors, router/group parental controls, and advanced parental/access actions.

## Optional Router Support

GL.iNet firmware varies by model and firmware generation. The integration treats WireGuard, cellular, repeater, SMS, Tailscale, ZeroTier, firewall, MCU battery, MCU OLED, and Parental & Access Control as optional modules. During setup you can choose which of these optional features to enable, and unsupported or unavailable APIs are skipped without failing setup.

If you disable all optional features, the integration still registers core router status sensors and entities. 

## Diagnostics & Troubleshooting

The integration provides a fully sanitized diagnostics export.
You can download diagnostics directly from the device page in Home Assistant. The generated JSON file will safely mask all sensitive data including your MAC addresses, WiFi passwords, session IDs, and tokens.

## Performance & Load Management

To alleviate the heavy load on small travel routers during polling, the integration uses sequential API execution. Instead of blasting the router with multiple simultaneous JSON-RPC payloads every scan interval, requests are processed sequentially. This acts as a native rate-limiter and prevents HTTP server stutters or timeouts on the router.
Furthermore, disabling unused features (via the Options Flow) completely removes those API calls from the loop, further reducing router CPU load.

### Dynamic Configuration & Cleanup

The integration dynamically manages its footprint based on your selections in the **Configure** menu:
- **Entity Cleanup**: When a feature is disabled, the integration automatically removes any associated entities from the Home Assistant Entity Registry.
- **Firewall Cleanup**: Disabling the firewall feature also removes port forwarding entities, avoiding orphaned `port_forwards` sensors.
- **MCU Cleanup**: Disabling MCU Battery removes battery sensors. Disabling MCU OLED removes OLED actions.
- **Action Cleanup**: Services (Actions) are registered at the domain level. If a feature (like SMS) is disabled across all configured routers, the corresponding services are automatically removed from Home Assistant to keep the UI clean.
