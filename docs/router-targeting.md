# Targeting a Specific Router

All `glinet_router` services accept an optional `mac` parameter. When multiple GL.iNet routers are configured in Home Assistant, you can use the router's MAC address to target a specific instance. If omitted, the first available hub is used.

## Usage

```yaml
action: glinet_router.send_sms
data:
  mac: 94:83:C4:00:11:22
  recipient: "+15551234567"
  text: "Hello from Home Assistant"
```

## Notes

- The MAC address must match the value reported by the integration for that router (visible in the integration device's **Settings**).
- If only one router is configured, the `mac` parameter can be omitted.
- Unknown or mismatched MAC addresses result in a Home Assistant service error.

## Related Pages

- [Services & Actions](services.md) — How to use Home Assistant services with this integration.
- [Refresh Clients](refresh-clients.md) — The `refresh_clients` service.
