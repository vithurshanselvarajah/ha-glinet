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

- [Hub Overview](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/hub) — Index of Hub reference pages.
- [Data Fetching](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/hub-data-fetching) — Per-feature polling functions.
- [Action Functions](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/hub-action-functions) — Hub action methods.
- [Option Updates](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/hub-option-updates) — Runtime options handling.
- [Parental Control Helpers](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/hub-parental-helpers) — Group lookup and access control helpers.
