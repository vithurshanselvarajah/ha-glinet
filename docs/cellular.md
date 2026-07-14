# Cellular (Optional Feature)

The **Cellular** feature enables signal and network monitoring for GL.iNet routers equipped with internal or USB cellular modems.

## Setup Configuration

To enable this feature, check the **Cellular** option under **Enabled Features** in the integration configuration or options flow.

- **Option key**: `cellular`
- **Firmware support**: Firmware 4.8.x uses the aggregate modem API. Firmware 4.9+
  uses the newer per-slot modem API and is normalized to the same Home Assistant
  sensor attributes.

---

## Exposed Entities

### Sensors

| Entity | Description | API Source |
| --- | --- | --- |
| **Cellular WAN IPv4** | The IP address assigned to the cellular internet interface. Hidden when cellular internet is unavailable. | `modem/get_status` or 4.9+ normalized modem status |
| **Cellular WAN IPv6** | The IPv6 address assigned to the cellular internet interface. Hidden when cellular internet is unavailable. | `modem/get_status` or 4.9+ normalized modem status |
| **Cellular signal** | Overall cellular signal strength percentage. | `modem/get_status` or 4.9+ normalized modem status |
| **Cellular RSSI** | Received Signal Strength Indicator in dBm. | `modem/get_status` or 4.9+ normalized modem status |
| **Cellular RSRP** | Reference Signal Received Power in dBm. | `modem/get_status` or 4.9+ normalized modem status |
| **Cellular RSRQ** | Reference Signal Received Quality in dB. | `modem/get_status` or 4.9+ normalized modem status |
| **Cellular SINR** | Signal-to-Interference-plus-Noise Ratio in dB. | `modem/get_status` or 4.9+ normalized modem status |
| **Cellular band** | Active frequency band / service type (e.g., LTE Band 4). | `modem/get_status` or 4.9+ normalized modem status |
| **Cellular network** | Active mobile network operator name and connection mode. | `modem/get_status` or 4.9+ normalized modem status |
| **Cellular APN** | Access Point Name used for the cellular connection. | `modem/get_status` or 4.9+ normalized modem status |

---

## Developer Reference

For details on how the modem APIs are queried and parsed, see the [Modem API Coverage](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/modem-api) documentation.
