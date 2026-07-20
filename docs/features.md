# Feature Matrix & Supported Actions

This page provides an overview of the core features always provided by the GL.iNet integration. Optional features are documented on their own dedicated pages — see the [Home](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/Home) page for the full list.

## Core Features

The following capabilities are always available regardless of optional feature selection:

- **Config Flow & Discovery**: Easy setup with DHCP discovery support.
- **Router Device Metadata**: Model, firmware version, and MAC address.
- **System Monitoring**: CPU temperature, load averages (1m, 5m, 15m), memory usage, flash usage, and uptime sensors.
- **WAN Status Sensors**: Per-interface WAN status sensors (e.g., Ethernet, Repeater, Cellular, Tethering). Each sensor reports `Up`, `Down`, or `Unknown` for its interface. Configurable via the **WAN Status Monitors** option.
- **WiFi Controls**: Switches to enable/disable each configured WiFi interface.
- **System LED**: Switch to toggle the router's physical status LED.
- **Reboot Control**: Button to restart the router immediately.
- **Device Tracking**: Monitors connected clients — MAC address, name/alias, IP address, interface type, and last-seen timestamp. Includes a cleanup mechanism for stale offline devices.
- **Connected Clients Count**: Sensor showing total currently active tracked clients.
- **Client Diagnostics**: Per-client download rate, upload rate, and IP address sensors attached to each tracked client device.
- **Unknown Device Management**: Discover unknown devices, auto-cleanup rules, allow/blocklist controls, and manual MAC address entries. See [Unknown Device Management](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/unknown-devices).
- **Firmware Updates**: Native Home Assistant firmware update entity with release notes when the router exposes them.
- **Sanitized Diagnostics**: Safe diagnostic downloads masking sensitive data (MAC addresses, WiFi passwords, session IDs, and tokens).

## Optional Features

The integration treats several advanced capabilities as optional modules selectable during setup or via the **Configure** menu:

- [Cellular](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/cellular) - Monitor cellular connection, signals, and modem diagnostics.
- [Repeater](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/repeater) - Connect to and scan for external WiFi networks, manage saved networks.
- [SMS](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/sms) - Send, receive, and delete text messages.
- [Tailscale](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/tailscale) - Enable or disable Tailscale integration.
- [WireGuard Client](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/wireguard-client) - Toggle configured WireGuard client profiles.
- [WireGuard Server](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/wireguard-server) - Manage the built-in WireGuard server.
- [OpenVPN Client](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/openvpn-client) - Manage and select OpenVPN client configurations.
- [OpenVPN Server](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/openvpn-server) - Manage the built-in OpenVPN server.
- [ZeroTier](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/zerotier) - Enable or disable ZeroTier VPN connections.
- [AdGuard Home](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/adguard-home) - Enable/disable AdGuard Home and DNS redirection.
- [KMWAN](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/kmwan) - Read and update GL.iNet's KMWAN multi-WAN configuration through actions.
- [MWAN3](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/mwan3) - Read and update MWAN3 multi-WAN configuration through actions.
- [Firewall](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/firewall) - Manage firewall rules, port forwarding, and DMZ settings.
- [Smart Fan](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/smart-fan) - Monitor fan status, speed, and set temperature thresholds.
- [MCU Battery](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/mcu-battery) - Monitor battery status and configure high/low temperature warnings.
- [MCU OLED](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/mcu-oled) - Configure what is displayed on the router's OLED screen.
- [Parental & Access Control](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/parental-control) - Manage internet access blocks and parental group rules per client.
- [API Playground](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/playground) - Send custom JSON-RPC or ubus commands and inspect the response.

If you disable all optional features, the integration still registers all core router status sensors and entities.

## Setup Configuration Options

When adding the GL.iNet integration or modifying it via the **Configure** menu, the following options are available:

- **Router URL**: The network address of your router (e.g., `http://192.168.8.1`). HTTPS is supported if configured on the router.
- **Admin Password**: The password for the `root` account used to access the GL.iNet admin panel.
- **Update Interval**: The polling frequency in seconds, between 10s and 300s (default 30s). Increase this if you experience router slowdowns.
- **Faster updates (parallel fetching)**: When enabled, the per-feature API requests are fired concurrently during each coordinator refresh using `asyncio.gather`. This can significantly reduce total refresh time on capable hardware but puts more load on the router — keep it off (the default) for low-powered travel routers. Errors raised by a single fetch are logged and do not abort the rest of the refresh.
- **Consider Home**: The grace period in seconds before a device is marked as "Away". Prevents devices from flickering when they briefly drop off the network.
- **Discover unknown devices**: When enabled, adds all newly discovered devices to the Home Assistant device registry rather than only known/tracked ones. Toggling this off automatically cleans up untracked devices.
- **Auto-cleanup unknown devices (min)**: The inactivity period in minutes after which an untracked device is automatically removed from the registry. Set to `0` to disable.
- **Unknown Devices Filter Mode**: Select whether the list of unknown devices behaves as a whitelist or blacklist.
- **Select Unknown Devices**: Select from currently discovered unknown devices to whitelist or blacklist (only available in the options flow).
- **Manual MAC Address List (One per line)**: Manually enter MAC addresses (one per line) of unknown devices to whitelist or blacklist.
- **WAN Status Monitors**: Select which WAN interface/protocol combinations to monitor (e.g., `Ethernet 1 IPv4`, `Cellular IPv4`). Defaults to all detected interfaces for both IPv4 and IPv6. Deselect individual entries to hide those sensors and reduce polling overhead.
- **Enabled Features**: Select which optional modules to activate for this router instance, including optional WAN policy controls.

## Authentication & Session Management

To ensure reliable communication and minimise session expiration issues:

- **Proactive Refresh**: The integration refreshes the session token at the start of every polling cycle.
- **Retry Mechanism**: Token renewal is retried up to 3 times on authentication or token errors.
- **Detailed Logging**: Failed renewals log the specific error response or exception for easier troubleshooting.
- **Graceful Failure**: If all retries fail, a re-authentication flow is triggered in Home Assistant to prompt the user for credentials.

## Polling

The integration is a **local polling** integration (`iot_class: local_polling`) and uses Home Assistant's `DataUpdateCoordinator` to refresh router state on a single, user-configurable interval.

- **Default polling interval**: 30 seconds, controlled by the **Update Interval** option.
- **Allowed range**: 10–300 seconds. The config flow clamps the value to this range so the user cannot pick a value that would hammer the router.
- **Coordinator-driven**: All entity platforms (sensors, switches, binary sensors, select, update, device tracker) read their state from a single coordinator update per cycle. This avoids each platform polling independently and keeps router load predictable.
- **Sequential fetch**: Within a single update, the hub calls each JSON-RPC endpoint one at a time. This is intentional — see **Performance & Load Management** below. Users with capable routers can opt into concurrent execution via the **Faster updates (parallel fetching)** option in the config / options flow.
- **Throttled firmware check**: Firmware upgrade metadata is refreshed at most once every 24 hours even if the polling interval is much shorter.
- **Single source of truth for connection health**: A single failed token renewal or transient timeout does not stop the rest of the cycle. Errors are caught at the request boundary, surfaced through `UpdateFailed`, and the coordinator retries at the next interval.

If you have a slow router (e.g., a low-end travel router) or you see timeouts in the log, raise the **Update Interval** to 60–120 seconds. If you want near-real-time device tracking, lower it to 10–15 seconds — but be aware this increases the number of JSON-RPC calls per minute.

## Performance & Load Management

To reduce load on small travel routers, the integration uses sequential API execution — requests are processed one at a time rather than in parallel. This acts as a native rate-limiter and prevents HTTP server stutters or timeouts on the router.

Disabling unused optional features via the **Configure** menu completely removes those API calls from the polling loop, further reducing router CPU load. The integration also dynamically cleans up entities when features are disabled:

- **Entity Cleanup**: Disabling a feature automatically removes its associated entities from the Home Assistant Entity Registry.
- **Firewall Cleanup**: Disabling the Firewall feature also removes port forwarding entities.
- **MCU Cleanup**: Disabling MCU Battery removes battery sensors; disabling MCU OLED removes OLED actions.
- **Action Cleanup**: If a feature (e.g., SMS) is disabled across all configured routers, its services are automatically removed from Home Assistant.

## Diagnostics & Troubleshooting

The integration provides a fully sanitized diagnostics export. Download it directly from the device page in Home Assistant — the generated JSON file safely masks all sensitive data including MAC addresses, WiFi passwords, session IDs, and tokens.
