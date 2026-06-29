# API Playground

The **API Playground** is an advanced feature that allows you to interact directly with the GL.iNet router's JSON-RPC/ubus API. By using the `ha_glinet.playground` service, you can execute custom API methods and receive the raw JSON responses directly in Home Assistant.

> [!WARNING]
> This is an advanced feature intended for developers and power users. Sending invalid commands or parameters can alter your router's configuration, interrupt network connectivity, or cause reboot loops. Use with caution.

---

## Enabling the API Playground

Because the playground allows arbitrary commands to be executed on the router, it is **disabled by default**. To enable it:

1. In Home Assistant, go to **Settings > Devices & Services**.
2. Find the **GL-INet** integration cards.
3. Click **Configure** on the router instance you wish to use.
4. In the features checklist, check the box next to **API Playground**.
5. Click **Submit** to save changes.

Once enabled, the `ha_glinet.playground` service will be registered and available to call from Developer Tools, automations, and scripts.

---

## Action Structure

The `ha_glinet.playground` service takes the following fields:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `method` | String | Yes | The JSON-RPC or ubus method to invoke (e.g., `system/get_info` or `challenge`). |
| `body` | Object / Dict | No | The JSON/YAML parameters to pass with the method. |
| `mac` | String | No | The router MAC address to target (optional if you only have one router configured). |

### Request Routing Logic
The playground automatically handles your session cookie/token (`sid`) behind the scenes:
* **Ubus calls (Slash syntax)**: If your method contains a slash (e.g., `module/method`), it is treated as a ubus call. The integration compiles this into a JSON-RPC `call` request:
  `{"method": "call", "params": [sid, "module", "method", body]}`.
* **Top-Level Methods**: If your method does not contain a slash (e.g., `challenge` or `login`), it is sent directly as a top-level RPC method:
  `{"method": "method", "params": body}`.

---

## Examples

Below are multiple examples demonstrating how to call the playground service using YAML and the structure of the JSON responses you can expect.

### Example 1: Retrieve System Status (`system/get_status`)
This calls the `get_status` method of the `system` ubus module to fetch router uptime, memory info, temperature, and load average.

**Service Call YAML:**
```yaml
action: ha_glinet.playground
data:
  method: "system/get_status"
```

**Returned Response Data:**
```json
{
  "system": {
    "uptime": 86400,
    "loadavg": [0.05, 0.12, 0.08],
    "memory_total": 256000000,
    "memory_free": 128000000
  },
  "cpu": {
    "temperature": 48
  }
}
```

---

### Example 2: Retrieve Firewall Zone List (`firewall/get_zone_list`)
This fetches the lists of defined network security zones on your router.

**Service Call YAML:**
```yaml
action: ha_glinet.playground
data:
  method: "firewall/get_zone_list"
```

**Returned Response Data:**
```json
{
  "zones": [
    {
      "name": "lan",
      "input": "ACCEPT",
      "output": "ACCEPT",
      "forward": "ACCEPT"
    },
    {
      "name": "wan",
      "input": "REJECT",
      "output": "ACCEPT",
      "forward": "REJECT"
    }
  ]
}
```

---

### Example 3: Toggle Status LED Configuration (`led/set_config` with boolean body)
This toggles the router's physical front LED panel on or off.

**Service Call YAML (Turn off LED):**
```yaml
action: ha_glinet.playground
data:
  method: "led/set_config"
  body:
    led_enable: false
```

**Returned Response Data:**
```json
{
  "result": 0
}
```

---

### Example 4: Get VPN Status (`vpn-client/get_status` on 4.8+ firmware)
This retrieves the connection state of active VPN tunnels on newer GL.iNet firmware.

**Service Call YAML:**
```yaml
action: ha_glinet.playground
data:
  method: "vpn-client/get_status"
```

**Returned Response Data:**
```json
{
  "status_list": [
    {
      "type": "wireguard",
      "peer_id": 1,
      "status": 1,
      "ip": "10.0.0.2"
    }
  ]
}
```

---

### Example 5: Request Challenge Salt (`challenge` unauthenticated top-level call)
This calls the unauthenticated top-level `challenge` method to query authentication algorithms and salt for a user.

**Service Call YAML:**
```yaml
action: ha_glinet.playground
data:
  method: "challenge"
  body:
    username: "root"
```

**Returned Response Data:**
```json
{
  "alg": 6,
  "salt": "$6$abcdefgh",
  "nonce": "123456789abcdef",
  "hash-method": "sha256"
}
```
