# Tailscale (Optional Feature)

The **Tailscale** feature allows you to monitor and control the Tailscale VPN service on your GL.iNet router.

## Setup Configuration

To enable this feature, check the **Tailscale** option under **Enabled Features** in the integration configuration or options flow.

- **Option key**: `tailscale`

---

## Exposed Entities

### Switches

| Entity | Description | API Source |
| --- | --- | --- |
| **Tailscale** | Toggles the Tailscale service on or off. Only created when Tailscale is configured on the router. | `tailscale/get_status` / `tailscale/set_config` |

## Related Pages

- [Services & Actions](services.md) — How to use Home Assistant services with this integration.
- [Entity Reference](entities.md) — All core and optional entities.
