# WireGuard Server (Optional Feature)

The **WireGuard Server** feature allows you to monitor and control the WireGuard server running on your GL.iNet router.

## Setup Configuration

To enable this feature, check the **WireGuard Server** option under **Enabled Features** in the integration configuration or options flow.

- **Option key**: `wg_server`

---

## Exposed Entities

### Sensors

| Entity | Description | API Source |
| --- | --- | --- |
| **WireGuard server users** | Count of currently online WireGuard server peers/clients. | `wg-server/get_status` |

### Switches

| Entity | Description | API Source |
| --- | --- | --- |
| **WG Server** | Toggles the WireGuard server on or off. | `wg-server/start` / `wg-server/stop` |
