# Firewall (Optional Feature)

The **Firewall** feature allows you to monitor firewall rule and port forward counts, manage DMZ and WAN access toggles, and add/remove custom rules.

## Setup Configuration

To enable this feature, check the **Firewall** option under **Enabled Features** in the integration configuration or options flow.

- **Option key**: `firewall`

> **Note**: Disabling this feature also removes all port forwarding entities, avoiding orphaned `port_forwards` sensors.

---

## Exposed Entities

### Sensors

| Entity | Description | API Source |
| --- | --- | --- |
| **Firewall rules** | Count of active custom firewall rules. | `firewall/get_rules` |
| **Port forwards** | Count of active port forwarding rules. | `firewall/get_port_forwards` |

### Switches

| Entity | Description | API Source |
| --- | --- | --- |
| **Firewall DMZ** | Toggle the DMZ (DeMilitarized Zone) feature. | `firewall/set_dmz` |
| **WAN Ping Access** | Toggle whether the router responds to ICMP echo requests from the WAN. | `firewall/set_wan_access` |
| **WAN HTTPS Access** | Toggle remote HTTPS management access from the WAN. | `firewall/set_wan_access` |
| **WAN SSH Access** | Toggle remote SSH management access from the WAN. | `firewall/set_wan_access` |

---

## Actions (Services)

The following services are registered under the `glinet_router` domain when the Firewall feature is enabled:

### `add_firewall_rule`
Adds a custom firewall rule.

- **`name`**: Descriptive name for the rule.
- **`src`**: Source zone (e.g., `wan`, `lan`).
- **`src_ip`** (Optional): Source IP address.
- **`src_mac`** (Optional): Source MAC address.
- **`src_port`** (Optional): Source port.
- **`proto`**: Protocol (`tcp`, `udp`, `tcpudp`).
- **`dest`**: Destination zone.
- **`dest_ip`** (Optional): Destination IP address.
- **`dest_port`** (Optional): Destination port.
- **`target`**: Target action (`ACCEPT`, `DROP`, `REJECT`).
- **`enabled`**: Whether the rule is active.
- **`mac`** (Optional): Target a specific router by MAC address.

### `remove_firewall_rule`
Removes a firewall rule.

- **`rule_id`**: The ID of the rule to remove.
- **`mac`** (Optional): Target a specific router by MAC address.

### `get_firewall_rules`
Returns configured firewall rules as action response data.

- **`mac`** (Optional): Target a specific router by MAC address.

**Response**: `rules` array, each item containing `id` and `name`.

### `add_port_forward`
Adds a port forwarding rule.

- **`name`**: Descriptive name.
- **`src`**: Source zone (usually `wan`).
- **`src_dport`**: External port.
- **`proto`**: Protocol.
- **`dest`**: Destination zone (usually `lan`).
- **`dest_ip`**: Internal IP address.
- **`dest_port`**: Internal port.
- **`enabled`**: Whether the rule is active.
- **`mac`** (Optional): Target a specific router by MAC address.

### `remove_port_forward`
Removes a port forwarding rule.

- **`rule_id`** (Optional): The ID of the rule to remove.
- **`remove_all`** (Optional): If `true`, removes all port forwarding rules.
- **`mac`** (Optional): Target a specific router by MAC address.

### `set_dmz`
Configures DMZ settings.

- **`enabled`**: Whether DMZ is enabled.
- **`dest_ip`** (Optional): The internal IP address to expose.
- **`mac`** (Optional): Target a specific router by MAC address.
