# OpenVPN Server (Optional Feature)

The **OpenVPN Server** feature allows you to monitor and control the OpenVPN server running on your GL.iNet router.

## Setup Configuration

To enable this feature, check the **OpenVPN Server** option under **Enabled Features** in the integration configuration or options flow.

- **Option key**: `ovpn_server`

---

## Exposed Entities

### Sensors

| Entity | Description | API Source |
| --- | --- | --- |
| **OpenVPN server users** | Count of currently online connected OpenVPN server users. | `ovpn-server/get_status` |

### Switches

| Entity | Description | API Source |
| --- | --- | --- |
| **OpenVPN Server** | Toggles the OpenVPN server on or off. | `ovpn-server` API |
