# Cellular (Optional Feature)

The **Cellular** feature enables signal and network monitoring for GL.iNet routers equipped with internal or USB cellular modems.

## Setup Configuration

To enable this feature, check the **Cellular** option under **Enabled Features** in the integration configuration or options flow.

- **Option key**: `cellular`
- **Firmware support**:
  - **Firmware 4.8.x** uses the aggregate modem API (`modem/get_status` and
    `modem/get_info`). The APN, signal metrics, and the cellular WAN IP
    all come from that single response.
  - **Firmware 4.9+** uses the newer per-slot modem API. Several changes:
    - The 4.9 firmware dropped the legacy **overall signal strength**
      and **RSSI** readings — the corresponding Home Assistant sensors
      (`Cellular signal`, `Cellular RSSI`) are no longer registered, and
      the **Cellular network** sensor (which duplicated `Cellular band`)
      is removed entirely. Existing installs have these entities
      cleaned up automatically on the next reload.
    - The cellular WAN IP is sourced from the bodyless
      `modem/get_network_info` call, which returns the IPv4/IPv6 lease
      per active SIM slot under `networks[].ipv4` / `networks[].ipv6`.
    - The APN is no longer carried on the modem status payload. The
      integration now issues a per-bus `modem/get_sim_config` call
      (keyed by ICCID) and merges the APN onto each modem's `simcard`
      so the `Cellular APN` sensor keeps working unchanged.
    - The `kmwan/get_status` response keeps `modem_0001` as a logical
      aggregate that the firmware always reports as Down
      (`status_v4: 1`). The real link state is published under the
      per-slot interfaces `modem_0001_s1` / `modem_0001_s2`. The
      integration transparently resolves the cellular `WanStatusSensor`
      to the active per-slot interface on 4.9+ so the `Cellular status`
      sensor shows Up when the cellular link is actually up.

---

## Exposed Entities

### Sensors

| Entity | Description | 4.8 source | 4.9+ source |
| --- | --- | --- | --- |
| **Cellular WAN IPv4** | The IP address assigned to the cellular internet interface. Hidden when cellular internet is unavailable. | `modem.get_status` → `modems[].network.ipv4.ip` | Bodyless `modem/get_network_info` → `networks[].ipv4.ip` (per active SIM slot). |
| **Cellular WAN IPv6** | The IPv6 address assigned to the cellular internet interface. Hidden when cellular internet is unavailable. | `modem.get_status` → `modems[].network.ipv6.ip` | Bodyless `modem/get_network_info` → `networks[].ipv6.ip`. |
| **Cellular APN** | Access Point Name used for the cellular connection. | `modem.get_status` → `modems[].simcard.apn` | Per-bus `modem/get_sim_config` → ICCID-keyed record → `apn`. |
| **Cellular band** | Active frequency band / service type (e.g., `LTE Band 4`). | `modem.get_status` → `modems[].simcard.band` | `modem.get_status` → `modems[].simcard.band` (preserved in 4.9 normalised status). |
| **Cellular RSRP** | Reference Signal Received Power in dBm. | `modem.get_status` → `modems[].simcard.signal.rsrp` | `modem.get_status` → `modems[].simcard.signal.rsrp`. |
| **Cellular RSRQ** | Reference Signal Received Quality in dB. | `modem.get_status` → `modems[].simcard.signal.rsrq` | `modem.get_status` → `modems[].simcard.signal.rsrq`. |
| **Cellular SINR** | Signal-to-Interference-plus-Noise Ratio in dB. | `modem.get_status` → `modems[].simcard.signal.sinr` | `modem.get_status` → `modems[].simcard.signal.sinr`. |

> **Removed sensors**: `Cellular signal`, `Cellular RSSI`, and `Cellular network` are no longer registered. The 4.9 firmware no longer surfaces the underlying values for the first two, and `Cellular network` duplicated `Cellular band`. The `Cellular band` sensor above is the canonical replacement.

### WAN Status Sensors

A `WanStatusSensor` is created for every interface in the `kmwan/get_status` response that you monitor (see the **Wan Status Monitors** option in the integration configuration).

On firmware 4.8 there is a single `Cellular status` sensor backed by the `modem_0001` interface.

On firmware 4.9 there are additional per-slot sensors:
- `Cellular status` — backed by `modem_0001` (the aggregate). The integration resolves this to the active per-slot interface (`modem_0001_s1` or `modem_0001_s2`) so the sensor correctly shows Up when the cellular link is up.
- `Cellular SIM 1 status` — backed by `modem_0001_s1`.
- `Cellular SIM 2 status` — backed by `modem_0001_s2`.

The `Cellular status` sensor's `extra_state_attributes` include:
- `interface` — the actual interface name the sensor read from (e.g. `modem_0001_s1` on 4.9+, `modem_0001` on 4.8).
- `interface_name` — the display label (e.g. `Cellular SIM 1`).
- `requested_interface` — the original interface name the sensor was registered with (always `modem_0001` for the cellular status sensor).
- `ipv4_status` / `ipv6_status` — the human-readable Up/Down/Unknown per protocol.
- `status_v4` / `status_v6` — the raw firmware values (`0` = Up, `1` = Down).

---

## 4.9+ Modem Data Flow

Each `fetch_cellular_status` refresh issues the following JSON-RPC calls (4.9 firmware only):

| # | Method | Body | Purpose |
| --- | --- | --- | --- |
| 1 | `modem/get_modem_current_interface` | `{}` | Discovers the active SIM targets (`modem_0001_s1`, `modem_0001_s2`). |
| 2 | `modem/get_signals` | `{"time": 10}` | Rolling signal-strength history per slot (used for the band/RSSI/strength metrics). |
| 3 | `modem/get_network_status` | `{}` (bodyless) | Aggregated dial / status info for every active network. |
| 4 | `modem/get_network_info` | `{}` (bodyless) | Per-slot IPv4/IPv6 lease + cell-info (band, RSRP, RSRQ, SINR, mode). |
| 5 | `modem/get_sim_config` (per bus) | `{"bus": "0001:01:00.0"}` | ICCID-keyed SIM records carrying the APN. One call per distinct modem bus. |

Steps 3 and 4 use the bodyless form on 4.9 — the response carries a `networks` array with one entry per active slot, indexed by `(bus, slot)`. The integration tries every bus alias for each target so the short logical bus (`0001`) and the full PCI bus (`0001:01:00.0`) both resolve to the same modem record.

If the bodyless call returns no entries for a target, the integration falls back to the per-target request shape (`{"bus": ..., "slot": ...}`) so older 4.9 builds that haven't flipped the endpoint still work.

---

## Migration Notes (4.8 → 4.9+)

When upgrading from firmware 4.8 to 4.9, the following entity-registry changes happen automatically on the next Home Assistant reload:

- **`Cellular signal`**, **`Cellular RSSI`**, **`Cellular network`** — removed from the entity registry. These sensors are no longer registered, and any existing entities from a prior 4.8 install are cleaned up by the hub's `async_initialize_hub` pass.
- **`Cellular status`** — the unique_id is unchanged (`glinet_sensor/<device_mac>/wan_status_modem_0001`), so the existing entity keeps its history. On 4.9+ the sensor now resolves to the active per-slot interface and reports the real Up/Down state.
- **`Cellular WAN IPv4` / `Cellular WAN IPv6`** — the unique_ids are unchanged, and the IP values are now sourced from the bodyless `modem/get_network_info` call.
- **`Cellular APN`** — the unique_id is unchanged, and the APN is now sourced from `modem/get_sim_config` on 4.9+.

---

## Developer Reference

For details on how the modem APIs are queried and parsed, see the [Modem API Coverage](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/modem-api) documentation.

## Related Pages

- [Modem API Coverage](modem-api.md) — Details on how the modem APIs are queried and parsed.
- [Services & Actions](services.md) — How to use Home Assistant services with this integration.
- [Entity Reference](entities.md) — All core and optional entities.
