# Smart Fan Controls

Some GL.iNet routers expose fan status and temperature settings through the device API. When that data is available, the integration surfaces it in Home Assistant.

## What you get

- A binary sensor showing whether the fan is currently running.
- A sensor for the current fan speed in RPM.
- A diagnostic sensor for the configured fan trigger temperature.
- A number entity that lets you set the trigger temperature used by the router.

## Setup

No separate feature toggle is required for this support. It is available automatically when the router reports fan data.

## Configuration

Use the fan trigger temperature number entity to adjust the threshold for the router's fan behavior. The integration also shows the current threshold and fan speed as attributes where supported.

## Service

The integration registers a service named `set_fan_temperature`.

### `set_fan_temperature`

Sets the router fan threshold temperature.

- **`temperature`**: The new trigger temperature in Celsius.
- **`mac`** (Optional): Target a specific router by MAC address.

Example:

```yaml
action: glinet_router.set_fan_temperature
data:
  temperature: 70
```
