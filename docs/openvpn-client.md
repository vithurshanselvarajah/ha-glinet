# OpenVPN Client (Optional Feature)

The **OpenVPN Client** feature surfaces every configured OpenVPN client profile on your GL.iNet router as a switch so you can turn individual tunnels on or off.

## Setup Configuration

To enable this feature, check the **OpenVPN Client** option under **Enabled Features** in the integration configuration or options flow.

- **Option key**: `ovpn_client`

## Exposed Entities

### Switches

| Entity | Description | API Source |
| --- | --- | --- |
| **OpenVPN client switches** | One switch per configured OpenVPN client profile returned by the router. Toggles the specific client connection on or off. | `ovpn-client` API |

The active client profile and its location are stored on the router but are not exposed as Home Assistant entities. They can be read directly from the router's web UI.

## Related Pages

- [Services & Actions](services.md) — How to use Home Assistant services with this integration.
- [Entity Reference](entities.md) — All core and optional entities.
