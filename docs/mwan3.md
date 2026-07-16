# MWAN3 (Optional Feature)

The **MWAN3** feature reads and updates the standard OpenWrt MWAN3 multi-WAN configuration through services. Use this when your router is configured with the upstream MWAN3 package rather than the GL.iNet-native KMWAN.

## Setup Configuration

To enable this feature, check the **MWAN3** option under **Enabled Features** in the integration configuration or options flow.

- **Option key**: `mwan3`

## Actions (Services)

The following services are registered under the `glinet_router` domain when the MWAN3 feature is enabled:

### `mwan3_get_config`

Retrieves the current MWAN3 configuration from the router. Supports response data.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `mac` | string | No | Target a specific router by MAC address. |

### `mwan3_get_status`

Retrieves the current MWAN3 interface status. Supports response data.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `mac` | string | No | Target a specific router by MAC address. |

### `mwan3_set_config`

Updates the MWAN3 configuration.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `config` | object | Yes | New MWAN3 configuration. |
| `mac` | string | No | Target a specific router by MAC address. |

### `mwan3_set_interface`

Updates a single MWAN3 interface.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `interface` | object | Yes | Interface definition to update. |
| `mac` | string | No | Target a specific router by MAC address. |

## Related Pages

- [KMWAN](kmwan.md) — GL.iNet's preferred multi-WAN policy engine.
- [Router API Notes](router-api.md) — Endpoints, authentication, and module inventory.
