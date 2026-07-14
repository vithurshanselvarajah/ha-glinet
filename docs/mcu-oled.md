# MCU OLED (Optional Feature)

The **MCU OLED** feature allows you to configure what information is displayed on the built-in OLED screen of GL.iNet travel routers that support it.

## Setup Configuration

To enable this feature, check the **MCU OLED** option under **Enabled Features** in the integration configuration or options flow.

- **Option key**: `mcu_oled`

> **Note**: Disabling this feature removes all MCU OLED actions.

---

## Actions (Services)

The following services are registered under the `glinet_router` domain when the MCU OLED feature is enabled:

### `get_mcu_oled_config`
Retrieves the current OLED screen display configuration from the router. Supports response data.

- **`mac`** (Optional): Target a specific router by MAC address.

**Response**: Returns the current `screen_display` configuration flags.

### `set_mcu_oled_config`
Updates sections displayed on the MCU OLED screen. Omitted fields retain their current router values.

- **`main`** (Optional): Toggle showing the main screen.
- **`wifi_password`** (Optional): Toggle showing the WiFi password.
- **`wifi_2g`** (Optional): Toggle showing 2.4 GHz WiFi status.
- **`wifi_5g`** (Optional): Toggle showing 5 GHz WiFi status.
- **`lan`** (Optional): Toggle showing LAN network status.
- **`vpn`** (Optional): Toggle showing VPN connection status.
- **`custom`** (Optional): Toggle showing custom display content.
- **`content`** (Optional): Custom display content or command string.
- **`mac`** (Optional): Target a specific router by MAC address.
