# MCU OLED (Optional Feature)

The **MCU OLED** feature allows you to configure what information is displayed on the built-in OLED screen of GL.iNet travel routers that support it.

## Setup Configuration

To enable this feature, check the **MCU OLED** option under **Enabled Features** in the integration configuration or options flow.

- **Option key**: `mcu_oled`

> Disabling this feature removes all MCU OLED actions.

## Actions (Services)

The following services are registered under the `glinet_router` domain when the MCU OLED feature is enabled:

### `get_mcu_oled_config`

Retrieves the current OLED screen display configuration from the router. Supports response data.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `mac` | string | No | Target a specific router by MAC address. |

**Response**: Returns the current `screen_display` configuration flags.

### `set_mcu_oled_config`

Updates sections displayed on the MCU OLED screen. Omitted fields retain their current router values.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `main` | boolean | No | Toggle showing the main screen. |
| `wifi_password` | boolean | No | Toggle showing the WiFi password. |
| `wifi_2g` | boolean | No | Toggle showing 2.4 GHz WiFi status. |
| `wifi_5g` | boolean | No | Toggle showing 5 GHz WiFi status. |
| `lan` | boolean | No | Toggle showing LAN network status. |
| `vpn` | boolean | No | Toggle showing VPN connection status. |
| `custom` | boolean | No | Toggle showing custom display content. |
| `content` | string | No | Custom display content or command string. |
| `mac` | string | No | Target a specific router by MAC address. |

## Related Pages

- [Services & Actions](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/services) — How to use Home Assistant services with this integration.
- [Entity Reference](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/entities) — All core and optional entities.
