# Hub Logic (`hub.py`)

The `GLinetHub` class coordinates communication between Home Assistant and the router. It manages the session lifecycle, error handling, and periodic polling (30s).

## Core Functions

| Function | Purpose |
| --- | --- |
| `async_initialize_hub` | Performs late initialization (fetching model/MAC) and starts the polling interval. |
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
| `fetch_wireguard_clients` | Tracks the connection status and tunnel IDs for WireGuard VPN profiles. |
| `fetch_tailscale_state` | Monitors the status of the Tailscale service. |
| `fetch_cellular_status` | Aggregates modem hardware info with live SIM signal/network status. |
| `fetch_sms_messages` | Retrieves and parses the SMS inbox into internal models. |

## Action Functions

| Function | Purpose |
| --- | --- |
| `send_sms` | Sends an SMS message using the first available SMS-capable modem bus. |
| remove_sms | Deletes a specific SMS message using the message identifier. |