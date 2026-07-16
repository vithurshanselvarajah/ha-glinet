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
| `modem/get_traffic_config` | Reads the per-SIM cumulative traffic counters and (optional) data-limit configuration. The 4.8 response uses flat keys: `sim{slot}_traffic_total` and `sim{slot}_limit` (`enable`, `threshold`, `unit`, `reset_period`, `day`, `hour`, `month`). |

### Firmware 4.9+

Firmware 4.9 changes the modem read model from aggregate `get_info` / `get_status`
responses to slot-focused endpoints. The integration detects firmware `4.9.0` and
newer from `system/get_info` and normalizes the new responses back into the existing
`{"modems": [...]}` shape used by the sensors.

| API | Purpose |
| --- | --- |
| `modem/get_modem_current_interface` | Discovers active modem interface names. The integration maps names such as `modem_0001_s1` to `bus: "0001", slot: 1`. On the user's 4.9 router the response carries one entry per active SIM slot (e.g. `modem_0001_s1`, `modem_0001_s2`). |
| `modem/get_signals` | Reads per-slot signal values such as RSRP, RSRQ, SINR, strength, and network type. The integration issues one bodyless call per refresh and indexes the response by slot. |
| `modem/get_network_status` (bodyless) | Reads per-slot dial status, ICCID, protocol, and traffic counters. The 4.9 firmware exposes this as a **bodyless** call — the response carries a `networks` array with one entry per active slot. |
| `modem/get_network_info` (bodyless) | Reads per-slot IP address data (IPv4/IPv6 lease, gateway, DNS), network interface name, and cell information (band, mode, RSRP, RSRQ, SINR). The 4.9 firmware exposes this as a **bodyless** call — the response carries a `networks` array with one entry per active slot. |
| `modem/get_sim_config` | Reads the per-SIM APN and configuration. The 4.9 firmware exposes this as a **per-bus** call — the integration issues one call per distinct modem bus and merges the ICCID-keyed APN onto each modem's `simcard` record. |
| `modem/get_sms_list` | Lists SMS messages. On 4.9+ the integration calls this once per discovered bus. |
| `modem/get_traffic_config` | Reads the per-SIM cumulative traffic counters and (optional) data-limit configuration. The 4.9 response shape uses two arrays: `traffic[].{slot, type, traffic_total}` for the per-SIM traffic totals and `limit[].{slot, type, enable, threshold, unit, reset_period, day, hour, month}` for the per-SIM data limit. The integration sends the bus taken from the discovered modem record (e.g. `"0001"` for `modem_0001_s1` / `modem_0001_s2`); the literal `"cpu"` is only used as a placeholder when the firmware returns no per-slot interfaces. |

#### Bodyless request shape (4.9+)

The 4.9 bodyless calls have **empty params** and return every active network in a
single response. Example for `modem/get_network_info`:

```json
{
  "method": "call",
  "jsonrpc": "2.0",
  "params": ["<sid>", "modem", "get_network_info", {}],
  "id": 0
}
```

Response:

```json
{
  "result": {
    "ret": 0,
    "resp": "Success",
    "networks": [
      {
        "network_interface": "modem_0001_s1",
        "bus": "0001:01:00.0",
        "slot": "1",
        "ipv4": {
          "ip": "10.77.58.41",
          "gateway": "10.77.58.42",
          "netmask": "255.255.255.252",
          "dns": ["188.31.250.128", "188.31.250.129"]
        },
        "cell_info": {
          "mode": "NR5G-NSA",
          "band": 78,
          "rsrp": "-86",
          "rsrq": "-10",
          "sinr": "22"
        }
      }
    ]
  }
}
```

The integration indexes the bodyless response by `(bus, slot)` and tries every bus
alias for each target so the short logical bus (`0001`) and the full PCI bus
(`0001:01:00.0`) both resolve to the same modem record. If the bodyless response
returns no entries for a given target, the integration falls back to the per-target
request shape (`{"bus": ..., "slot": ...}`) so older 4.9 builds that haven't
flipped the endpoint still work.

#### Per-bus SIM config (4.9+)

The 4.9 firmware exposes the APN through a separate per-bus call:

```json
{
  "method": "call",
  "jsonrpc": "2.0",
  "params": ["<sid>", "modem", "get_sim_config", {"bus": "0001:01:00.0"}],
  "id": 0
}
```

Response:

```json
{
  "result": {
    "8944200204977051694F": {
      "manual": true,
      "username": "",
      "pincode": "",
      "ip_type": 1,
      "cid": 1,
      "roaming": false,
      "apn": "mob.asm.net",
      "password": "",
      "auth": "NONE"
    }
  }
}
```

The response is keyed by ICCID. The integration picks the record whose ICCID matches
the modem's ICCID (falling back to the first record) and copies the `apn` (plus
other SIM fields when present) onto the modem's `simcard` so the `Cellular APN`
sensor continues to resolve the value.

## Write APIs Used

| API | Purpose |
| --- | --- |
| `modem/send_sms` | Sends SMS using modem `bus`, `phone_number`, `body`, and `timeout`. On 4.9+ the integration includes `slot` when one was discovered. |
| `modem/remove_sms` | Deletes SMS. The integration uses `scope: 10` with the message `name` for a single-message delete and includes `slot` on 4.9+ when known. |

## SMS Error Codes

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
