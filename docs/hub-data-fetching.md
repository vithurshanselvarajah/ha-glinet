# Hub Data Fetching Functions

These methods are called during the coordinator update cycle to pull data from the router and refresh the cached state.

| Function | Purpose |
| --- | --- |
| `fetch_system_status` | Updates CPU temperature, load averages, memory, flash statistics, uptime, and MCU battery data. |
| `fetch_kmwan_status` | Updates per-interface WAN status (Ethernet, Repeater, Cellular, Tethering) via the `edgerouter` API. |
| `fetch_upgrade_info` | Pulls the latest firmware check data from the router, using fields such as `current_version`, `current_compile_time`, and `current_type`, along with release notes, upgrade config, and live upgrade status for the update entity. This refresh is performed once every 24 hours rather than on every polling cycle. |
| `fetch_connected_devices` | Polls the client list and calculates traffic rates for tracked devices. |
| `fetch_wifi_interfaces` | Retrieves configuration and status for all WiFi radios (2.4GHz, 5GHz, etc.). |
| `fetch_fan_status` | Retrieves current fan speed, running state, and temperature threshold. |
| `fetch_led_status` | Retrieves current system LED enabled state. |
| `fetch_wireguard_clients` | Tracks the connection status and tunnel IDs for WireGuard VPN profiles. |
| `fetch_wg_server_status` | Retrieves the status and connected peers for the WireGuard server. |
| `fetch_ovpn_clients` | Tracks the connection status for OpenVPN clients. |
| `fetch_ovpn_server_status` | Retrieves the status and connected users for the OpenVPN server. |
| `fetch_tailscale_state` | Monitors the status of the Tailscale service. |
| `fetch_zerotier_status` | Monitors the status of the ZeroTier service. |
| `fetch_adguard_status` | Monitors AdGuard Home and DNS status. |
| `fetch_cellular_status` | Aggregates modem hardware info with live SIM signal/network status. |
| `fetch_repeater_status` | Updates the connection state, SSID, and signal for WiFi station mode. |
| `fetch_repeater_config` | Retrieves settings like band locking, auto-switch, and smart reconnect configuration. |
| `fetch_saved_networks` | Syncs the list of known WiFi access points used for repeater mode. |
| `fetch_firewall_rules` | Retrieves the list of custom firewall rules. |
| `fetch_dmz_config` | Retrieves the current DMZ configuration. |
| `fetch_port_forwards` | Retrieves the list of port forwarding rules. |
| `fetch_wan_access` | Retrieves WAN ping/HTTPS/SSH access settings. |
| `fetch_zone_list` | Retrieves the firewall zone list (used for DMZ targeting). |
| `fetch_parental_control_status` | Retrieves parental control config, group status, and filtering mode. |
| `fetch_access_control_config` | Retrieves the blacklist/whitelist access control configuration. |
| `fetch_sms_messages` | Retrieves and parses the SMS inbox into internal models. |

## Related Pages

- [Hub Overview](hub.md)
- [Hub Core Functions](hub-core.md)
- [Action Functions](hub-action-functions.md)
- [Option Updates](hub-option-updates.md)
- [Parental Control Helpers](hub-parental-helpers.md)
