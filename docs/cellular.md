# Cellular (Optional Feature)

The **Cellular** feature enables signal and network monitoring for GL.iNet routers equipped with internal or USB cellular modems.

## Setup Configuration

To enable this feature, check the **Cellular** option under **Enabled Features** in the integration configuration or options flow.

- **Option key**: `cellular`

---

## Exposed Entities

### Sensors

| Entity | Description | API Source |
| --- | --- | --- |
| **WAN IP** | The IP address assigned to the cellular internet interface. Hidden when cellular internet is unavailable. | `modem/get_status` |
| **Cellular signal** | Overall cellular signal strength percentage. | `modem/get_status` |
| **Cellular RSSI** | Received Signal Strength Indicator in dBm. | `modem/get_status` |
| **Cellular RSRP** | Reference Signal Received Power in dBm. | `modem/get_status` |
| **Cellular RSRQ** | Reference Signal Received Quality in dB. | `modem/get_status` |
| **Cellular SINR** | Signal-to-Interference-plus-Noise Ratio in dB. | `modem/get_status` |
| **Cellular band** | Active frequency band / service type (e.g., LTE Band 4). | `modem/get_status` |
| **Cellular network** | Active mobile network operator name and connection mode. | `modem/get_status` |
| **Cellular APN** | Access Point Name used for the cellular connection. | `modem/get_status` |

---

## Developer Reference

For details on how the modem APIs are queried and parsed, see the [Modem API Coverage](https://github.com/vithurshanselvarajah/ha-glinet/wiki/modem-api) documentation.
