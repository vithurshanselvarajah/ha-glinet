# Runtime State & Poller (Hub)

The `GLinetHub` class inherits from `DataUpdateCoordinator` and manages communication between Home Assistant and the router. It handles the session lifecycle, error handling, and periodic polling (user-configurable, default 30s).

This page indexes the Hub reference documentation, split by function category.

## Pages

| Page | Description |
| --- | --- |
| [Hub Core Functions](hub-core.md) | Coordinator lifecycle, session refresh, and API invocation helpers. |
| [Data Fetching Functions](hub-data-fetching.md) | Per-feature polling methods invoked during each update. |
| [Action Functions](hub-action-functions.md) | Methods that write to the router or trigger a router-side behavior. |
| [Option Updates](hub-option-updates.md) | Runtime application of configuration option changes. |
| [Parental Control Helpers](hub-parental-helpers.md) | Group lookup and access control helper methods. |
