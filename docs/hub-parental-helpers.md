# Hub Parental Control Helpers

These properties and methods are used internally by entities and service handlers to look up parental groups and check internet access state.

| Property / Method | Purpose |
| --- | --- |
| `parental_groups` | Returns a `dict` of `ParentalGroup` objects keyed by group ID. |
| `parental_group_by_name_or_id` | Looks up a `ParentalGroup` by either its ID or display name (case-insensitive). Returns `None` when no match is found. |
| `parental_group_for_device` | Returns the `ParentalGroup` that currently contains a given client MAC, or `None`. |
| `device_internet_access_enabled` | Returns whether a given MAC currently has internet access based on the active access control mode (black/white list). |

## Related Pages

- [Hub Overview](hub.md)
- [Hub Core Functions](hub-core.md)
- [Data Fetching](hub-data-fetching.md)
- [Action Functions](hub-action-functions.md)
- [Option Updates](hub-option-updates.md)
