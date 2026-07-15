# Port Forwards (Optional Feature)

The **Port Forwards** feature lets you add and remove port forwarding rules on your GL.iNet router. Forwarded ports route external traffic from the WAN to a specific internal host and port.

## Setup Configuration

To enable this feature, check the **Firewall** option under **Enabled Features** in the integration configuration or options flow.

- **Option key**: `firewall`

> Disabling this feature also removes the `Port forwards` sensor and the related firewall rule entities.

## Sensors

| Entity | Description | API Source |
| --- | --- | --- |
| **Port forwards** | Count of active port forwarding rules. | `firewall/get_port_forwards` |

## Actions (Services)

The following services are registered under the `glinet_router` domain when the Firewall feature is enabled:

### `add_port_forward`

Adds a port forwarding rule.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | string | Yes | Descriptive name. |
| `src` | string | Yes | Source zone (usually `wan`). |
| `src_dport` | string | Yes | External port. |
| `proto` | string | Yes | Protocol (`tcp`, `udp`, `tcpudp`). |
| `dest` | string | Yes | Destination zone (usually `lan`). |
| `dest_ip` | string | Yes | Internal IP address. |
| `dest_port` | string | Yes | Internal port. |
| `enabled` | boolean | No | Whether the rule is active. Defaults to `true`. |
| `mac` | string | No | Target a specific router by MAC address. |

Example:

```yaml
action: glinet_router.add_port_forward
data:
  name: Web server
  src: wan
  src_dport: "8443"
  proto: tcp
  dest: lan
  dest_ip: 192.168.8.50
  dest_port: "443"
```

### `remove_port_forward`

Removes a port forwarding rule. If `remove_all` is `true`, all port forwarding rules are removed and `rule_id` is ignored.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `rule_id` | string | No | The ID of the rule to remove. |
| `remove_all` | boolean | No | If `true`, removes all port forwarding rules. |
| `mac` | string | No | Target a specific router by MAC address. |

## Related Pages

- [Firewall Rules](firewall-rules.md) — Add and remove custom firewall rules.
- [DMZ](dmz.md) — Toggle the DMZ feature.
- [WAN Access](wan-access.md) — Toggle WAN ping, HTTPS, and SSH access.
- [Firewall parent page](firewall.md)
