# Modem API Coverage

This page summarizes the GL.iNet SDK 4.0 modem API behavior used by the integration.

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

| API | Purpose |
| --- | --- |
| `modem/get_info` | Lists modem hardware, bus identifiers, ports, SIM data, SMS support, IMEI, modem name/version/vendor. |
| `modem/get_status` | Lists modem status, current SIM, SIM registration, carrier, signal, network state, IP data, traffic counters, unread SMS count. |
| `modem/get_sms_list` | Lists SMS messages with identifier, phone number, text, and timestamp. |

## Write APIs Used

| API | Purpose |
| --- | --- |
| `modem/send_sms` | Sends SMS using modem `bus`, `phone_number`, `body`, and `timeout`. |
| `modem/remove_sms` | Deletes SMS. The integration uses `scope: 10` with the message `name` for a single-message delete. |

## SMS Error Codes

`modem/send_sms` may return:

- `-1`: Cellular modem was not found
- `-2`: Unknown error
- `-3`: Sending failed
- `-4`: Sending timeout
- `-5`: Cellular modem does not support SMS
- `-6`: Current network environment does not support SMS

## Bus Selection

Most modem APIs require `bus`. The integration selects a default bus by:

1. Prefer a modem from `modem/get_info` with `sms_support: true`.
2. Otherwise prefer a modem with SIM card data.
3. Otherwise use the first modem returned by the router.

## APIs Not Exposed

The modem PDF also documents mutating APIs for reconnecting, auto-connect, SIM config, tower locking, traffic limits, firmware upgrade, and SIM unlock. Those are not exposed yet because they can disrupt router connectivity or require more UI/confirmation work.
