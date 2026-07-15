# Hub Core Functions

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

## Related Pages

- [Hub Overview](hub.md) — Index of Hub reference pages.
- [Data Fetching](hub-data-fetching.md) — Per-feature polling functions.
- [Action Functions](hub-action-functions.md) — Hub action methods.
- [Option Updates](hub-option-updates.md) — Runtime options handling.
- [Parental Control Helpers](hub-parental-helpers.md) — Group lookup and access control helpers.
