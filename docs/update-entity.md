# Firmware Update

The integration exposes a native Home Assistant update entity that surfaces the router's current firmware version and online upgrade metadata.

| Entity | Source | Notes |
| --- | --- | --- |
| **Firmware** | `upgrade/check_firmware_online`, `upgrade/get_config`, `upgrade/upgrade_online` | Native Home Assistant firmware update entity. Shows release notes when available and only exposes install when the router provides the required download metadata. |

## Notes

- Release notes are pulled from the router's online firmware metadata when available.
- Install is only exposed when the router provides the required download metadata.

## Related Pages

- [Entity Reference parent page](entities.md)
- [Buttons](buttons.md) — Reboot and fan test buttons.
