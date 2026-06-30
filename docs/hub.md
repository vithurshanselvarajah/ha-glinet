# Runtime State & Poller (Hub)

The `GLinetHub` class inherits from `DataUpdateCoordinator` and manages communication between Home Assistant and the router. It handles the session lifecycle, error handling, and periodic polling (user-configurable, default 30s).

## Core Functions

| Function | Purpose |
| --- | --- |
| `_async_update_data` | The entry point for the coordinator update. Triggers `fetch_all_data`. |
| `async_initialize_hub` | Performs late initialization (fetching model/MAC) and cleans up orphan entities for disabled features. |
| `refresh_session_token` | Authenticates with the router RPC and updates the active session ID. Retries up to 3 times on failure. |
| `fetch_all_data` | Sequentially triggers all data update functions listed below. |
| `_invoke_api` | Internal wrapper for core API calls; handles timeouts, token renewal, and error logging. |
| `_invoke_optional_api` | Wrapper for API calls that may not exist on all models (e.g., fan, modem). Silently skips on failure. |

## Data Fetching Functions

| Function | Purpose |
| --- | --- |
| `fetch_system_status` | Updates CPU temperature, load averages, memory, flash statistics, uptime, and MCU battery data. |
| `fetch_kmwan_status` | Updates per-interface WAN status (Ethernet, Repeater, Cellular, Tethering) via the `edgerouter` API. |
| `fetch_upgrade_info` | Pulls the latest firmware check data, release notes, upgrade config, and live upgrade status for the update entity. |
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

## Action Functions

| Function | Purpose |
| --- | --- |
| `reboot` | Triggers a router reboot. |
| `set_wifi_interface_enabled` | Enables or disables a WiFi interface. |
| `start_vpn_client` / `stop_vpn_client` | Controls WireGuard client connections. |
| `start_wg_server` / `stop_wg_server` | Controls the WireGuard server. |
| `start_ovpn_client` / `stop_ovpn_client` / `stop_all_ovpns` | Controls OpenVPN client connections. |
| `start_ovpn_server` / `stop_ovpn_server` | Controls the OpenVPN server. |
| `connect_tailscale` / `disconnect_tailscale` | Controls the Tailscale connection. |
| `start_zerotier` / `stop_zerotier` | Controls the ZeroTier connection. |
| `set_led_enabled` | Controls the system LED. |
| `set_adguard_enabled` / `set_adguard_dns_enabled` | Controls AdGuard Home functionality. |
| `add_firewall_rule` / `remove_firewall_rule` | Adds or removes a custom firewall rule. |
| `get_firewall_rule_summaries` | Returns a list of `{id, name}` dicts for all current firewall rules. |
| `add_port_forward` / `remove_port_forward` | Adds or removes a port forwarding rule. |
| `set_dmz_config` | Enables or disables the DMZ and optionally sets the target IP. |
| `set_wan_access` | Updates WAN ping/HTTPS/SSH access settings. |
| `set_fan_temperature` | Sets the fan activation temperature threshold. |
| `test_fan` | Runs the fan at full speed for a short diagnostic test. |
| `get_kmwan_config` / `get_kmwan_status` / `set_kmwan_config` / `set_kmwan_interface` / `set_kmwan_sensitivity` | Reads and updates KMWAN configuration through the optional WAN policy services. |
| `get_mwan3_config` / `get_mwan3_status` / `set_mwan3_config` / `set_mwan3_interface` | Reads and updates MWAN3 configuration through the optional WAN policy services. |
| `upgrade_firmware` | Starts a firmware update using the router's latest online firmware metadata when available. |
| `send_sms` | Sends an SMS message using the first available SMS-capable modem bus. |
| `remove_sms` | Deletes SMS messages by scope or specific message ID. |
| `scan_wifi_networks` | Triggers a site survey and updates the list of available SSIDs. |
| `connect_to_wifi` | Configures and initiates a repeater connection. |
| `disconnect_wifi` | Terminates the current repeater connection. |
| `get_saved_wifi_networks` | Returns the current list of saved repeater AP profiles. |
| `remove_saved_wifi_network` | Deletes a specific saved profile from the router. |
| `get_mcu_battery_config` / `set_mcu_battery_config` | Reads or writes battery warning thresholds. |
| `get_mcu_oled_config` / `set_mcu_oled_config` | Reads or writes OLED screen display settings. |
| `set_parental_control_enabled` | Globally enables or disables parental controls. |
| `set_group_enabled` | Enables or disables internet limits for a specific parental group. |
| `set_temporary_override` | Applies a temporary parental control override to a group. |
| `set_parental_mode` | Sets the router's parental filtering mode. |
| `update_parental_signatures` | Triggers a parental control signature database update. |
| `set_access_control_mode` | Switches between blacklist and whitelist access control modes. |
| `set_single_device_block` | Blocks or unblocks a specific client device by MAC address. |
| `set_group_schedules_enabled` | Enables or disables schedule enforcement for a parental group. |
| `assign_device_to_parental_group` | Moves a client device into a specific parental group. |
| `set_repeater_auto_switch` | Enables or disables repeater auto-switch between saved networks. |
| `set_repeater_smart_reconnect` | Enables or disables repeater smart reconnect logic. |
| `set_repeater_bare_mode` | Enters or exits repeater bare mode. |
| `set_repeater_band` | Sets the locked wireless band for repeater mode. |
