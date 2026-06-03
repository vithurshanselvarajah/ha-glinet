# WireGuard Client (Optional Feature)

The **WireGuard Client** feature allows you to toggle configured WireGuard client profiles on your GL.iNet router.

## Setup Configuration

To enable this feature, check the **WireGuard Client** option under **Enabled Features** in the integration configuration or options flow.

- **Option key**: `wg_client`

---

## Exposed Entities

### Switches

| Entity | Description | API Source |
| --- | --- | --- |
| **WireGuard client switches** | One switch per configured WireGuard client profile returned by the router. Toggles the specific connection profile on or off. | `wg-client` or `vpn-client` API, depending on firmware version. |

> **Note**: Newer GL.iNet firmware versions use the `vpn-client` API. Older firmware uses the `wg-client` API. The integration detects and uses the correct API automatically.
