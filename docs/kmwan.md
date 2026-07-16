# KMWAN (Optional Feature)

The **KMWAN** feature reads and updates the GL.iNet router's KMWAN multi-WAN configuration through services. KMWAN is GL.iNet's preferred multi-WAN policy engine.

## Setup Configuration

To enable this feature, check the **KMWAN** option under **Enabled Features** in the integration configuration or options flow.

- **Option key**: `kmwan`

## Actions (Services)

The following services are registered under the `glinet_router` domain when the KMWAN feature is enabled:

### `kmwan_get_config`

Retrieves the current KMWAN configuration from the router. Supports response data.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `mac` | string | No | Target a specific router by MAC address. |

### `kmwan_get_status`

Retrieves the current KMWAN interface status. Supports response data.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `mac` | string | No | Target a specific router by MAC address. |

### `kmwan_set_config`

Updates the KMWAN configuration.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `config` | object | Yes | New KMWAN configuration. |
| `mac` | string | No | Target a specific router by MAC address. |

### `kmwan_set_interface`

Updates a single KMWAN interface.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `interface` | object | Yes | Interface definition to update. |
| `mac` | string | No | Target a specific router by MAC address. |

### `kmwan_set_sensitivity`

Updates the KMWAN interface-failure sensitivity.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `sensitivity` | object | Yes | Sensitivity configuration. |
| `mac` | string | No | Target a specific router by MAC address. |

## Related Pages

- [MWAN3](mwan3.md) — Alternative multi-WAN policy engine.
- [Router API Notes](router-api.md) — Endpoints, authentication, and module inventory.
