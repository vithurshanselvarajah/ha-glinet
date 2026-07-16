# DMZ (Optional Feature)

The **DMZ** (DeMilitarized Zone) feature lets you toggle the router's DMZ mode and configure the internal destination IP address. When DMZ is enabled, all inbound traffic from the WAN that is not matched by another rule is forwarded to the configured host.

## Setup Configuration

To enable this feature, check the **Firewall** option under **Enabled Features** in the integration configuration or options flow.

- **Option key**: `firewall`

## Switches

| Entity | Description | API Source |
| --- | --- | --- |
| **Firewall DMZ** | Toggle the DMZ feature. The `destination_ip` attribute shows the currently configured target IP. | `firewall/set_dmz` |

## Actions (Services)

The following service is registered under the `glinet_router` domain when the Firewall feature is enabled:

### `set_dmz`

Configures DMZ settings.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `enabled` | boolean | Yes | Whether DMZ is enabled. |
| `dest_ip` | string | No | The internal IP address to expose. |
| `mac` | string | No | Target a specific router by MAC address. |

## Related Pages

- [Firewall Rules](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/firewall-rules) — Add and remove custom firewall rules.
- [Port Forwards](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/port-forwards) — Add and remove port forwarding rules.
- [WAN Access](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/wan-access) — Toggle WAN ping, HTTPS, and SSH access.
- [Firewall parent page](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/firewall)
