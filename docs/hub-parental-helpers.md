# Hub Parental Control Helpers

These properties and methods are used internally by entities and service handlers to look up parental groups and check internet access state.

| Property / Method | Purpose |
| --- | --- |
| `parental_groups` | Returns a `dict` of `ParentalGroup` objects keyed by group ID. |
| `parental_group_by_name_or_id` | Looks up a `ParentalGroup` by either its ID or display name (case-insensitive). Returns `None` when no match is found. |
| `parental_group_for_device` | Returns the `ParentalGroup` that currently contains a given client MAC, or `None`. |
| `device_internet_access_enabled` | Returns whether a given MAC currently has internet access based on the active access control mode (black/white list). |

## Related Pages

- [Hub Overview](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/hub)
- [Hub Core Functions](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/hub-core)
- [Data Fetching](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/hub-data-fetching)
- [Action Functions](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/hub-action-functions)
- [Option Updates](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/hub-option-updates)
