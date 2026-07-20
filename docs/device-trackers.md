# Device Trackers

Device trackers are created from online devices returned by the router API.

## Behavior

Trackers are created **only if the device is already known to Home Assistant** through another integration (e.g., the Mobile App, ESPHome, Zigbee, etc.). This prevents the integration from automatically adding every guest device, transient client, or unknown IoT device on your network as a new tracker entity.

However, you can enable the **Discover unknown devices** option during integration setup or in the options flow. When enabled, the integration tracks every device seen by the router, regardless of its status in the Home Assistant device registry.

To restrict which unknown devices are discovered, you can use the **Unknown Devices Filter Mode** (whitelist or blacklist). You can select devices from the dropdown (available in the options flow) or manually specify MAC addresses.

## Tracked Data

The tracker monitors:

- MAC address
- Name/alias
- IP address while online
- Interface type
- Last activity timestamp

Tracked devices use a `consider_home` logic (default 180s) to prevent entities from flickering to "Away" during brief client sleep cycles or router re-polls. Unhelpful tracker entities can be managed via the standard entity settings in **Settings → Devices & services**.

## Randomized MAC Addresses

If a device uses randomized MAC addresses, Home Assistant may see each randomized address as a separate tracker. Disable private/random MAC addressing for that WiFi network when you want stable tracking.

## Related Pages

- [Entity Reference parent page](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/entities)
- [Unknown Devices](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/unknown-devices) — Allow/blocklist controls for unknown devices.
