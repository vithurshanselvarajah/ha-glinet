# OpenVPN Client (Optional Feature)

The **OpenVPN Client** feature allows you to select the server location/profile and toggle configured OpenVPN client connections on your GL.iNet router.

## Setup Configuration

To enable this feature, check the **OpenVPN Client** option under **Enabled Features** in the integration configuration or options flow.

- **Option key**: `ovpn_client`

---

## Exposed Entities

### Selects

| Entity | Description | API Source |
| --- | --- | --- |
| **OpenVPN location** | Choose the server location configuration for the active OpenVPN client profile. | `ovpn-client/get_config` |

### Switches

| Entity | Description | API Source |
| --- | --- | --- |
| **OpenVPN client switches** | One switch per configured OpenVPN client profile returned by the router. Toggles the specific client connection on or off. | `ovpn-client` API |
