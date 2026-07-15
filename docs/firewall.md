# Firewall (Optional Feature)

The **Firewall** feature groups together everything related to the GL.iNet router's firewall: custom rules, port forwarding, the DMZ toggle, and remote WAN access settings. Each sub-feature is documented on its own page.

## Setup Configuration

To enable this feature, check the **Firewall** option under **Enabled Features** in the integration configuration or options flow.

- **Option key**: `firewall`

> Disabling this feature removes all firewall-related sensors, switches, and services from the registry.

## Sub-Features

| Page | Description |
| --- | --- |
| [Firewall Rules](firewall-rules.md) | Add and remove custom firewall rules. |
| [Port Forwards](port-forwards.md) | Add and remove port forwarding rules. |
| [DMZ](dmz.md) | Toggle the DMZ and configure the target IP. |
| [WAN Access](wan-access.md) | Toggle WAN ping, HTTPS, and SSH remote access. |
