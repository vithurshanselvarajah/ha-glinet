# WireGuard Client (Optional Feature)

The **WireGuard Client** feature allows you to toggle configured WireGuard client profiles on your GL.iNet router.

## Setup Configuration

To enable this feature, check the **WireGuard Client** option under **Enabled Features** in the integration configuration or options flow.

- **Option key**: `wg_client`

---

## Exposed Entities

The integration adapts to the router's firmware. On older firmware you get one switch per configured WireGuard profile; on 4.9 and newer you get one switch per dashboard tunnel.

### Firmware 4.8 and older

| Entity | Description | API Source |
| --- | --- | --- |
| **WireGuard client switches** | One switch per configured WireGuard client profile returned by the router. Toggles the specific connection profile on or off. | `wg-client` or legacy `vpn-client` API. |

### Firmware 4.9 and newer (VPN Dashboard)

Firmware 4.9 introduces a unified **VPN dashboard**. The integration only sees the WireGuard profiles that the router exposes on this dashboard — so **a new WireGuard client has to be added to the VPN Dashboard before it appears in Home Assistant**. Once it is on the dashboard the integration queries `vpn-client.get_tunnel` and surfaces one switch per dashboard tunnel whose `via.type` is `wireguard`.

> **Adding WireGuard profiles on 4.9+**:
> 1. Create / import the WireGuard profile in the router's admin UI as usual.
> 2. Open the **VPN Dashboard** section of the admin UI and **preconfigure** the profile onto a dashboard tunnel (assign it explicitly to a tunnel slot).
> 3. Reload the integration in Home Assistant. The new tunnel switch will appear under the **WireGuard Client** device.
>
> Do **not** simply toggle the profile on through the dashboard to "register" it. Toggling a tunnel that has no profile preconfigured overwrites the slot and leaves the existing configuration empty, which causes the integration to lose that tunnel. Always assign the profile to a tunnel slot before you toggle anything.

> **Removing WireGuard profiles on 4.9+**: if you remove (or unassign) a WireGuard profile from the VPN Dashboard on the router, the corresponding switch in Home Assistant is automatically removed on the next coordinator refresh. The dashboard should always reflect exactly what is currently configured on the router.

> **No profiles configured on the dashboard**: if you have not pre-configured any WireGuard profiles on the VPN dashboard, the router's firmware falls back to whatever tunnel was used last (or to the "default" / `novpn` tunnel) when a toggle is sent. The integration sends `vpn-client.set_tunnel` for the requested `tunnel_id`, but with no preconfigured profile the router will start whichever tunnel it currently considers the default. To get predictable, per-profile switches, preconfigure the WireGuard profiles on the VPN dashboard first.

| Entity | Description | API Source |
| --- | --- | --- |
| **WG Tunnel &lt;name&gt;** | One switch per dashboard tunnel. Reports the live link state from `vpn-client.get_status` and toggles the tunnel via `vpn-client.set_tunnel`. | `vpn-client` API (`get_tunnel`, `set_tunnel`, `get_status`). |

> **Backwards compatibility**: 4.8 routers keep the per-profile switches — the dashboard path activates only when the firmware reports version 4.9 or newer. Switching between firmware versions (downgrade or upgrade) may require reloading the integration so the entity registry picks the correct representation.

## Related Pages

- [Services & Actions](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/services) — How to use Home Assistant services with this integration.
- [Entity Reference](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/entities) — All core and optional entities.
