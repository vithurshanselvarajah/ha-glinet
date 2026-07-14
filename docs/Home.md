# glinet-router Documentation

Welcome to the `glinet-router` documentation. This wiki is meant to help you find the right guide quickly, whether you are setting up the integration for the first time or looking for a specific feature.

## For End Users

These pages cover what the integration provides, how to configure it, and how to use it in Home Assistant.

- [Feature Matrix](https://github.com/vithurshanselvarajah/glinet-router/wiki/features) - A quick overview of supported features and actions.
- [Entity Reference](https://github.com/vithurshanselvarajah/glinet-router/wiki/entities) - Detailed list of sensors, switches, buttons, and trackers.
- [Services & Actions](https://github.com/vithurshanselvarajah/glinet-router/wiki/services) - Guide on using Home Assistant services to control your router.
- [Automation Templates](https://github.com/vithurshanselvarajah/glinet-router/wiki/automations) - Ready-made automations you can paste into Home Assistant.
- [Smart Fan Controls](https://github.com/vithurshanselvarajah/glinet-router/wiki/smart-fan) - Fan status, speed, and temperature threshold controls.
- [Unknown Device Management](https://github.com/vithurshanselvarajah/glinet-router/wiki/unknown-devices) - Discovery, cleanup, and allow/blocklist handling for unknown devices.

### Optional Features

These pages cover configuration, entities, and services for optional modules that can be enabled on supported routers:

- [Cellular](https://github.com/vithurshanselvarajah/glinet-router/wiki/cellular) - Monitor cellular connection, signals, and modem diagnostics.
- [Repeater](https://github.com/vithurshanselvarajah/glinet-router/wiki/repeater) - Connect to and scan for external WiFi networks, manage saved networks.
- [SMS](https://github.com/vithurshanselvarajah/glinet-router/wiki/sms) - Send, receive, and delete text messages.
- [Tailscale](https://github.com/vithurshanselvarajah/glinet-router/wiki/tailscale) - Enable or disable Tailscale integration.
- [WireGuard Client](https://github.com/vithurshanselvarajah/glinet-router/wiki/wireguard-client) - Toggle configured WireGuard client profiles.
- [WireGuard Server](https://github.com/vithurshanselvarajah/glinet-router/wiki/wireguard-server) - Manage the built-in WireGuard server.
- [OpenVPN Client](https://github.com/vithurshanselvarajah/glinet-router/wiki/openvpn-client) - Manage and select OpenVPN client configurations.
- [OpenVPN Server](https://github.com/vithurshanselvarajah/glinet-router/wiki/openvpn-server) - Manage the built-in OpenVPN server.
- [ZeroTier](https://github.com/vithurshanselvarajah/glinet-router/wiki/zerotier) - Enable or disable ZeroTier VPN connections.
- [AdGuard Home](https://github.com/vithurshanselvarajah/glinet-router/wiki/adguard-home) - Enable/disable AdGuard Home and DNS redirection.
- [Firewall](https://github.com/vithurshanselvarajah/glinet-router/wiki/firewall) - Manage firewall rules, port forwarding, and DMZ settings.
- [MCU Battery](https://github.com/vithurshanselvarajah/glinet-router/wiki/mcu-battery) - Monitor battery status and configure high/low temperature warnings.
- [MCU OLED](https://github.com/vithurshanselvarajah/glinet-router/wiki/mcu-oled) - Configure what is displayed on the router's OLED screen.
- [Parental & Access Control](https://github.com/vithurshanselvarajah/glinet-router/wiki/parental-control) - Manage internet access blocks and parental group rules per client.
- [API Playground](https://github.com/vithurshanselvarajah/glinet-router/wiki/playground) - Send custom JSON-RPC or ubus commands and inspect the response.

## For Developers

These pages are aimed at the architecture, API details, and maintenance work behind the integration.

- [Developer Reference](https://github.com/vithurshanselvarajah/glinet-router/wiki/developer-reference) - Start here for contribution notes, tooling, and project structure.
- [Architecture](https://github.com/vithurshanselvarajah/glinet-router/wiki/architecture) - How the integration is structured and interacts with Home Assistant.
- [Runtime State & Poller (Hub)](https://github.com/vithurshanselvarajah/glinet-router/wiki/hub) - Details on the `GLinetHub` and `DataUpdateCoordinator`.
- [Router API Notes](https://github.com/vithurshanselvarajah/glinet-router/wiki/router-api) - Notes on the GL.iNet JSON-RPC API and authentication.
- [Modem API Coverage](https://github.com/vithurshanselvarajah/glinet-router/wiki/modem-api) - Details on the optional cellular modem API.
- [CI and Release Workflows](https://github.com/vithurshanselvarajah/glinet-router/wiki/ci-release) - How automated testing and releases work.
