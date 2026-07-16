# Hub Option Updates

These methods are used internally to apply configuration changes to a running hub, e.g. when the user changes options in the integration options flow.

| Function | Purpose |
| --- | --- |
| `apply_option_updates` | Merges new options into the running hub, rebuilds the effective settings, and adjusts the polling interval. Returns `True` on success. |

## Related Pages

- [Hub Overview](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/hub)
- [Hub Core Functions](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/hub-core)
- [Data Fetching](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/hub-data-fetching)
- [Action Functions](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/hub-action-functions)
- [Parental Control Helpers](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/hub-parental-helpers)
