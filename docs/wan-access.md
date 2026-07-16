# WAN Access (Optional Feature)

The **WAN Access** feature exposes switches for the three remote-access settings the GL.iNet router firewall supports: ICMP echo responses, HTTPS management, and SSH management.

## Setup Configuration

To enable this feature, check the **Firewall** option under **Enabled Features** in the integration configuration or options flow.

- **Option key**: `firewall`

## Switches

| Entity | Description | API Source |
| --- | --- | --- |
| **WAN Ping Access** | Toggle whether the router responds to ICMP echo requests from the WAN. | `firewall/set_wan_access` |
| **WAN HTTPS Access** | Toggle remote HTTPS management access from the WAN. | `firewall/set_wan_access` |
| **WAN SSH Access** | Toggle remote SSH management access from the WAN. | `firewall/set_wan_access` |

> WAN access switches are exposed only when the Firewall feature is enabled.

## Related Pages

- [Firewall Rules](firewall-rules.md) — Add and remove custom firewall rules.
- [Port Forwards](port-forwards.md) — Add and remove port forwarding rules.
- [DMZ](dmz.md) — Toggle the DMZ feature.
- [Firewall parent page](firewall.md)
