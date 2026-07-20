# ZeroTier (Optional Feature)

The **ZeroTier** feature allows you to monitor and toggle ZeroTier network connections on your GL.iNet router.

## Setup Configuration

To enable this feature, check the **ZeroTier** option under **Enabled Features** in the integration configuration or options flow.

- **Option key**: `zerotier`

> **Note**: Setting up ZeroTier requires you to first configure the Network ID directly on your GL.iNet router admin panel. Without a Network ID configured, the switch will not appear.

---

## Exposed Entities

### Switches

| Entity | Description | API Source |
| --- | --- | --- |
| **ZeroTier** | Toggles the ZeroTier service connection on or off. | `zerotier/get_status` / `zerotier/set_config` |

## Related Pages

- [Services & Actions](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/services) — How to use Home Assistant services with this integration.
- [Entity Reference](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/entities) — All core and optional entities.
