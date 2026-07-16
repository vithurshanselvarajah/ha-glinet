# Hub Action Functions

Action methods perform a write to the router or trigger a router-side behavior. Most are called from a Home Assistant service handler or entity's `async_turn_on` / `async_turn_off` hook.

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

## Related Pages

- [Hub Overview](hub.md)
- [Hub Core Functions](hub-core.md)
- [Data Fetching](hub-data-fetching.md)
- [Option Updates](hub-option-updates.md)
- [Parental Control Helpers](hub-parental-helpers.md)
