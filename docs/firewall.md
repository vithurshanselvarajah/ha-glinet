# Firewall (Optional Feature)

The **Firewall** feature groups together everything related to the GL.iNet router's firewall: custom rules, port forwarding, the DMZ toggle, and remote WAN access settings. Each sub-feature is documented on its own page.

## Setup Configuration

To enable this feature, check the **Firewall** option under **Enabled Features** in the integration configuration or options flow.

- **Option key**: `firewall`

> Disabling this feature removes all firewall-related sensors, switches, and services from the registry.

## Sub-Features

| Page | Description |
| --- | --- |
| [Firewall Rules](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/firewall-rules) | Add and remove custom firewall rules. |
| [Port Forwards](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/port-forwards) | Add and remove port forwarding rules. |
| [DMZ](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/dmz) | Toggle the DMZ and configure the target IP. |
| [WAN Access](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/wan-access) | Toggle WAN ping, HTTPS, and SSH remote access. |
