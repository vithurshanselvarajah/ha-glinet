# Firewall Rules (Optional Feature)

The **Firewall Rules** feature lets you add and remove custom firewall rules on your GL.iNet router. Rules are evaluated by the router's standard firewall pipeline.

## Setup Configuration

To enable this feature, check the **Firewall** option under **Enabled Features** in the integration configuration or options flow.

- **Option key**: `firewall`

> Disabling this feature also removes the `Firewall rules` sensor and the related port forwarding entities.

## Sensors

| Entity | Description | API Source |
| --- | --- | --- |
| **Firewall rules** | Count of active custom firewall rules. | `firewall/get_rules` |

## Actions (Services)

The following services are registered under the `glinet_router` domain when the Firewall feature is enabled:

### `add_firewall_rule`

Adds a custom firewall rule.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | string | Yes | Descriptive name for the rule. |
| `src` | string | Yes | Source zone (e.g., `wan`, `lan`). |
| `src_ip` | string | No | Source IP address. |
| `src_mac` | string | No | Source MAC address. |
| `src_port` | string | No | Source port. |
| `proto` | string | Yes | Protocol (`tcp`, `udp`, `tcpudp`). |
| `dest` | string | Yes | Destination zone. |
| `dest_ip` | string | No | Destination IP address. |
| `dest_port` | string | No | Destination port. |
| `target` | string | Yes | Target action (`ACCEPT`, `DROP`, `REJECT`). |
| `enabled` | boolean | No | Whether the rule is active. Defaults to `true`. |
| `mac` | string | No | Target a specific router by MAC address. |

### `remove_firewall_rule`

Removes a firewall rule.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `rule_id` | string | Yes | The ID of the rule to remove. |
| `mac` | string | No | Target a specific router by MAC address. |

### `get_firewall_rules`

Returns configured firewall rules as action response data.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `mac` | string | No | Target a specific router by MAC address. |

**Response**: `rules` array, each item containing `id` and `name`.

## Related Pages

- [Port Forwards](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/port-forwards) — Add and remove port forwarding rules.
- [DMZ](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/dmz) — Toggle the DMZ feature.
- [WAN Access](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/wan-access) — Toggle WAN ping, HTTPS, and SSH access.
- [Firewall parent page](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/firewall)
