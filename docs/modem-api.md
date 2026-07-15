# Modem API Coverage

This page summarizes the GL.iNet SDK 4.0 modem API behavior used by the integration.
The integration supports both the firmware 4.8 aggregate modem API and the firmware
4.9+ per-slot modem API.

The modem API uses the same JSON-RPC `/rpc` structure as the rest of the router API:

```json
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": ["<sid>", "modem", "<function>", { "...": "..." }],
  "id": 1
}
```

## Read APIs Used

### Firmware 4.8.x

| API | Purpose |
| --- | --- |
| `modem/get_info` | Lists modem hardware, bus identifiers, ports, SIM data, SMS support, IMEI, modem name/version/vendor. |
| `modem/get_status` | Lists modem status, current SIM, SIM registration, carrier, signal, network state, IP data, traffic counters, unread SMS count. |
| `modem/get_sms_list` | Lists SMS messages with identifier, phone number, text, and timestamp. |

### Firmware 4.9+

Firmware 4.9 changes the modem read model from aggregate `get_info` / `get_status`
responses to slot-focused endpoints. The integration detects firmware `4.9.0` and
newer from `system/get_info` and normalizes the new responses back into the existing
`{"modems": [...]}` shape used by the sensors.

| API | Purpose |
| --- | --- |
| `modem/get_modem_current_interface` | Discovers active modem interface names. The integration maps names such as `modem_1_1_s1` to `bus: "1-1", slot: 1`. |
| `modem/get_network_status` | Reads per-slot dial status, ICCID, protocol, and traffic counters. |
| `modem/get_network_info` | Reads per-slot IP address data, network interface, and cell information. |
| `modem/get_signals` | Reads per-slot signal values such as RSRP, RSRQ, SINR, strength, and network type. |
| `modem/get_sms_list` | Lists SMS messages. On 4.9+ the integration calls this once per discovered bus. |

## Write APIs Used

| API | Purpose |
| --- | --- |
| `modem/send_sms` | Sends SMS using modem `bus`, `phone_number`, `body`, and `timeout`. On 4.9+ the integration includes `slot` when one was discovered. |
| `modem/remove_sms` | Deletes SMS. The integration uses `scope: 10` with the message `name` for a single-message delete and includes `slot` on 4.9+ when known. |

## SMS Error Codes

`modem/send_sms` may return:

- `-1`: Cellular modem was not found
- `-2`: Unknown error
- `-3`: Sending failed
- `-4`: Sending timeout
- `-5`: Cellular modem does not support SMS
- `-6`: Current network environment does not support SMS

## Bus And Slot Selection

Most modem APIs require `bus`; firmware 4.9+ may also require `slot`. The integration
selects a default modem by:

1. Prefer a modem from `modem/get_info` with `sms_support: true`.
2. Otherwise prefer a modem with SIM card data.
3. Otherwise use the first modem returned by the router.

On firmware 4.9+, multiple logical modem records can share the same `bus`, so modem
records are keyed internally by `bus` plus `slot`. The public Home Assistant data still
exposes `default_bus` for compatibility and also includes `default_slot` when available.

## Firmware Compatibility Notes

- Firmware 4.8.x keeps using the original aggregate endpoints and sends the same SMS
  payloads as before.
- Firmware 4.9+ uses the new per-slot read endpoints and normalized output. Existing
  cellular sensors continue to read signal, network type, and IP data from the same
  Home Assistant attributes.
- If an individual 4.9 bus/slot probe reports that no modem exists, the integration skips
  that slot and continues polling the remaining discovered slots.

## APIs Not Exposed

The modem PDF also documents mutating APIs for reconnecting, auto-connect, SIM config, tower locking, traffic limits, firmware upgrade, and SIM unlock. Those are not exposed yet because they can disrupt router connectivity or require more UI/confirmation work.

## Related Pages

- [Cellular](cellular.md) — Cellular feature user reference.
- [Router API Notes](router-api.md) — Endpoints, authentication, and module inventory.
