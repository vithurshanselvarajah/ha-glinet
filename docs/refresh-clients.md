# Refresh Clients (Service)

The `refresh_clients` service forces the hub to immediately re-fetch the connected client list and request a coordinator refresh. This updates all dependent entities (device trackers, connected client counts, bandwidth sensors, etc.) without waiting for the next polling cycle.

## Setup Configuration

The `refresh_clients` service is always available regardless of optional feature selection.

## Actions (Services)

### `refresh_clients`

Forces the hub to immediately re-fetch the connected client list and request a coordinator refresh.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `mac` | string | No | Target a specific router by MAC address. |

Example:

```yaml
action: glinet_router.refresh_clients
```

## When to Use

- Right after adding or removing a client on the LAN.
- When Home Assistant device tracker states appear stale.
- After a router reboot to align the state with the current client list.

## Related Pages

- [Targeting a Specific Router](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/router-targeting)
- [Services & Actions parent page](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/services)
