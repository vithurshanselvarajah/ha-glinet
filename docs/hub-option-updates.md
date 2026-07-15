# Hub Option Updates

These methods are used internally to apply configuration changes to a running hub, e.g. when the user changes options in the integration options flow.

| Function | Purpose |
| --- | --- |
| `apply_option_updates` | Merges new options into the running hub, rebuilds the effective settings, and adjusts the polling interval. Returns `True` on success. |

## Related Pages

- [Hub Overview](hub.md)
- [Hub Core Functions](hub-core.md)
- [Data Fetching](hub-data-fetching.md)
- [Action Functions](hub-action-functions.md)
- [Parental Control Helpers](hub-parental-helpers.md)
