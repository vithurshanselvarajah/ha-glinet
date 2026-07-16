# Runtime State & Poller (Hub)

The `GLinetHub` class inherits from `DataUpdateCoordinator` and manages communication between Home Assistant and the router. It handles the session lifecycle, error handling, and periodic polling (user-configurable, default 30s).

This page indexes the Hub reference documentation, split by function category.

## Pages

| Page | Description |
| --- | --- |
| [Hub Core Functions](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/hub-core) | Coordinator lifecycle, session refresh, and API invocation helpers. |
| [Data Fetching Functions](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/hub-data-fetching) | Per-feature polling methods invoked during each update. |
| [Action Functions](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/hub-action-functions) | Methods that write to the router or trigger a router-side behavior. |
| [Option Updates](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/hub-option-updates) | Runtime application of configuration option changes. |
| [Parental Control Helpers](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/hub-parental-helpers) | Group lookup and access control helper methods. |
