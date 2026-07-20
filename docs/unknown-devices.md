# Unknown Device Management

The integration can help manage devices that appear on the network but are not yet part of your Home Assistant device registry.

## What this covers

- Discovering unknown devices during normal polling.
- Automatically cleaning up stale unknown devices after a period of inactivity.
- Choosing whether unknown devices should be treated as a whitelist or blacklist.
- Manually adding MAC addresses to the filter list.
- Selecting specific discovered devices from the options flow.

## Setup options

These options are available when adding the integration or changing it later via the Configure menu:

- **Add all devices**: When enabled, newly discovered devices are added to the device registry.
- **Cleanup devices**: Sets the inactivity period in minutes before untracked devices are removed.
- **Unknown devices filter mode**: Choose **Blacklist** or **Whitelist**.
- **Select unknown devices**: Pick discovered devices to include or exclude.
- **Manual MAC address list**: Add MAC addresses one per line for the filter list.

## How it works

When unknown device discovery is enabled, the integration evaluates each new device against the current filter rules. Devices that pass the rules are added to Home Assistant; those that do not are ignored or removed depending on the current cleanup settings.

## Notes

This feature is especially useful if you want Home Assistant to stay tidy and only track the devices you actually care about.

## Related Pages

- [Device Trackers](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/device-trackers) — Per-client device tracking.
- [Entity Reference](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/entities) — All core and optional entities.
