# AdGuard Home (Optional Feature)

The **AdGuard Home** feature allows you to control the integrated AdGuard Home ad-blocking service on your GL.iNet router.

## Setup Configuration

To enable this feature, check the **AdGuard Home** option under **Enabled Features** in the integration configuration or options flow.

- **Option key**: `adguard`

---

## Exposed Entities

### Switches

| Entity | Description | API Source |
| --- | --- | --- |
| **AdGuard Home** | Toggles the AdGuard Home service on or off. | `adguardhome/get_config` / `adguardhome/set_config` |
| **AdGuard Home DNS** | Toggles DNS redirection through AdGuard Home. | `adguardhome/get_config` / `adguardhome/set_config` |

## Related Pages

- [Services & Actions](services.md) — How to use Home Assistant services with this integration.
- [Entity Reference](entities.md) — All core and optional entities.
