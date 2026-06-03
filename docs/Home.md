# ha-glinet Documentation

Welcome to the `ha-glinet` documentation! To help you find what you need quickly, this wiki is divided into guides for End Users and references for Developers.

## For End Users

Information on what the integration provides, how to configure it, and how to use it in your Home Assistant setup.

- [Feature Matrix](https://github.com/vithurshanselvarajah/ha-glinet/wiki/features) - A high-level overview of supported features and actions.
- [Entity Reference](https://github.com/vithurshanselvarajah/ha-glinet/wiki/entities) - Detailed list of all sensors, switches, buttons, and trackers.
- [Services & Actions](https://github.com/vithurshanselvarajah/ha-glinet/wiki/services) - Guide on using Home Assistant services to control your router.

### Optional Features

These pages cover configuration, entities, and services for optional modules that can be enabled on supported routers:

- [Cellular](https://github.com/vithurshanselvarajah/ha-glinet/wiki/cellular) - Monitor cellular connection, signals, and modem diagnostics.
- [Repeater](https://github.com/vithurshanselvarajah/ha-glinet/wiki/repeater) - Connect to and scan for external WiFi networks, manage saved networks.
- [SMS](https://github.com/vithurshanselvarajah/ha-glinet/wiki/sms) - Send, receive, and delete text messages.
- [Tailscale](https://github.com/vithurshanselvarajah/ha-glinet/wiki/tailscale) - Enable or disable Tailscale integration.
- [WireGuard Client](https://github.com/vithurshanselvarajah/ha-glinet/wiki/wireguard-client) - Toggle configured WireGuard client profiles.
- [WireGuard Server](https://github.com/vithurshanselvarajah/ha-glinet/wiki/wireguard-server) - Manage the built-in WireGuard server.
- [OpenVPN Client](https://github.com/vithurshanselvarajah/ha-glinet/wiki/openvpn-client) - Manage and select OpenVPN client configurations.
- [OpenVPN Server](https://github.com/vithurshanselvarajah/ha-glinet/wiki/openvpn-server) - Manage the built-in OpenVPN server.
- [ZeroTier](https://github.com/vithurshanselvarajah/ha-glinet/wiki/zerotier) - Enable or disable ZeroTier VPN connections.
- [AdGuard Home](https://github.com/vithurshanselvarajah/ha-glinet/wiki/adguard-home) - Enable/disable AdGuard Home and DNS redirection.
- [Firewall](https://github.com/vithurshanselvarajah/ha-glinet/wiki/firewall) - Manage firewall rules, port forwarding, and DMZ settings.
- [MCU Battery](https://github.com/vithurshanselvarajah/ha-glinet/wiki/mcu-battery) - Monitor battery status and configure high/low temperature warnings.
- [MCU OLED](https://github.com/vithurshanselvarajah/ha-glinet/wiki/mcu-oled) - Configure what is displayed on the router's OLED screen.
- [Parental & Access Control](https://github.com/vithurshanselvarajah/ha-glinet/wiki/parental-control) - Manage internet access blocks and parental group rules per client.

## For Developers

Deep dives into the architecture, API clients, and contribution guidelines for maintaining or extending the integration.

- [Developer Reference](https://github.com/vithurshanselvarajah/ha-glinet/wiki/developer-reference) - Start here! Contribution guide, codebase structure, and tooling.
- [Architecture](https://github.com/vithurshanselvarajah/ha-glinet/wiki/architecture) - How the integration interacts with Home Assistant and the router.
- [Runtime State & Poller (Hub)](https://github.com/vithurshanselvarajah/ha-glinet/wiki/hub) - Details on the `GLinetHub` and `DataUpdateCoordinator`.
- [Router API Notes](https://github.com/vithurshanselvarajah/ha-glinet/wiki/router-api) - Notes on the GL.iNet JSON-RPC API and authentication.
- [Modem API Coverage](https://github.com/vithurshanselvarajah/ha-glinet/wiki/modem-api) - Details on the optional cellular modem API.
- [CI and Release Workflows](https://github.com/vithurshanselvarajah/ha-glinet/wiki/ci-release) - How automated testing and releases work.
