The `GLinetHub` class inherits from `DataUpdateCoordinator` and manages communication between Home Assistant and the router. It handles the session lifecycle, error handling, and periodic polling (30s).

## Core Functions

| Function | Purpose |
| --- | --- |
| `_async_update_data` | The entry point for the coordinator update. Triggers `fetch_all_data`. |
| `async_initialize_hub` | Performs late initialization (fetching model/MAC). |
| `refresh_session_token` | Authenticates with the router RPC and updates the active session ID. |
| `fetch_all_data` | Concurrently triggers all data update functions listed below. |
| `_invoke_api` | Internal wrapper for API calls; handles timeouts, token renewal, and error logging. |
| `_invoke_optional_api` | Wrapper for API calls that may not exist on all models (e.g., Modem). |

## Data Fetching Functions

| Function | Purpose |
| --- | --- |
| `fetch_system_status` | Updates CPU temperature, load averages, memory, and flash statistics. |
| `fetch_internet_status` | Updates WAN status, public IP, and connectivity state. |
| `fetch_connected_devices` | Polls the client list and calculates traffic rates for tracked devices. |
| `fetch_wifi_interfaces` | Retrieves configuration and status for all WiFi radios (2.4GHz, 5GHz, etc.). |
| `fetch_wireguard_clients` | Tracks the connection status and tunnel IDs for WireGuard VPN profiles when WireGuard support is enabled. |
| `fetch_tailscale_state` | Monitors the status of the Tailscale service. |
| `fetch_cellular_status` | Aggregates modem hardware info with live SIM signal/network status. |
| `fetch_repeater_status` | Updates the connection state, SSID, and signal for WiFi station mode. |
| `fetch_repeater_config` | Retrieves settings like band locking and auto-switch configuration. |
| `fetch_saved_networks` | Syncs the list of known WiFi access points used for repeater mode. |
| `fetch_sms_messages` | Retrieves and parses the SMS inbox into internal models. |

## Action Functions

| Function | Purpose |
| --- | --- |
| `send_sms` | Sends an SMS message using the first available SMS-capable modem bus. |
| `remove_sms` | Deletes a specific SMS message using the message identifier. |
| `scan_wifi_networks` | Triggers a site survey and updates the list of available SSIDs. |
| `connect_to_wifi` | Configures and initiates a repeater connection. |
| `disconnect_wifi` | Terminates the current repeater connection. |
| `remove_saved_wifi_network` | Deletes a specific saved profile from the router. |