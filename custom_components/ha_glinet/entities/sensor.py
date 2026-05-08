from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, EntityCategory, UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC, format_mac
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.util.dt import utcnow

from ..const import DOMAIN, FEATURE_CELLULAR, FEATURE_REPEATER, FEATURE_SMS
from ..models import RepeaterState
from ..utils import channel_to_band, get_first_int, get_first_value

if TYPE_CHECKING:
    from collections.abc import Callable

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from ..hub import GLinetHub
    from ..models import ClientDeviceInfo


@dataclass(frozen=True, kw_only=True)
class SystemStatusEntityDescription(SensorEntityDescription):
    value_fn: Callable[[dict[str, Any]], int | float | None]
    extra_attributes_fn: Callable[[dict[str, Any]], dict[str, Any]] | None = None


SYSTEM_SENSORS: tuple[SystemStatusEntityDescription, ...] = (
    SystemStatusEntityDescription(
        key="cpu_temp",
        name="CPU temperature",
        has_entity_name=True,
        icon="mdi:thermometer",
        entity_category=EntityCategory.DIAGNOSTIC,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value_fn=lambda system_status: (system_status.get("cpu") or {}).get("temperature"),
    ),
    SystemStatusEntityDescription(
        key="load_avg1",
        name="Load avg (1m)",
        has_entity_name=True,
        icon="mdi:cpu-64-bit",
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda status: (status.get("load_average") or [None])[0],
    ),
    SystemStatusEntityDescription(
        key="load_avg5",
        name="Load avg (5m)",
        has_entity_name=True,
        icon="mdi:cpu-64-bit",
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda status: (status.get("load_average") or [None, None])[1],
    ),
    SystemStatusEntityDescription(
        key="load_avg15",
        name="Load avg (15m)",
        has_entity_name=True,
        icon="mdi:cpu-64-bit",
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda status: (status.get("load_average") or [None, None, None])[2],
    ),
    SystemStatusEntityDescription(
        key="memory_use",
        name="Memory usage",
        has_entity_name=True,
        icon="mdi:memory",
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda status: _calc_usage_percent(
            status.get("memory_total"),
            status.get("memory_free"),
        ),
        extra_attributes_fn=lambda status: {
            "memory_total": status.get("memory_total"),
            "memory_free": status.get("memory_free"),
        },
    ),
    SystemStatusEntityDescription(
        key="flash_use",
        name="Flash usage",
        has_entity_name=True,
        icon="mdi:harddisk",
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda status: _calc_usage_percent(
            status.get("flash_total"),
            status.get("flash_free"),
        ),
        extra_attributes_fn=lambda status: {
            "flash_total": status.get("flash_total"),
            "flash_free": status.get("flash_free"),
        },
    ),
)


@dataclass(frozen=True, kw_only=True)
class HubSensorEntityDescription(SensorEntityDescription):
    value_fn: Callable[[GLinetHub], int | float | str | None]
    extra_attributes_fn: Callable[[GLinetHub], dict[str, Any]] | None = None


HUB_SENSORS: tuple[HubSensorEntityDescription, ...] = (
    HubSensorEntityDescription(
        key="connected_clients",
        name="Connected clients",
        has_entity_name=True,
        icon="mdi:devices",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda hub: hub.online_client_count,
    ),
    HubSensorEntityDescription(
        key="cellular_signal",
        name="Cellular signal",
        has_entity_name=True,
        icon="mdi:signal-cellular-2",
        native_unit_of_measurement="dBm",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda hub: get_first_int(
            hub.cellular_status,
            ("signal", "signal_strength", "rssi", "rsrp", "csq"),
            nested=("modem", "cellular", "sim", "signal"),
        ),
        extra_attributes_fn=lambda hub: hub.cellular_status,
    ),
    HubSensorEntityDescription(
        key="cellular_rssi",
        name="Cellular RSSI",
        has_entity_name=True,
        icon="mdi:signal-cellular-outline",
        native_unit_of_measurement="dBm",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda hub: get_first_int(
            hub.cellular_status,
            ("rssi",),
            nested=("modem", "cellular", "sim", "signal"),
        ),
    ),
    HubSensorEntityDescription(
        key="cellular_rsrp",
        name="Cellular RSRP",
        has_entity_name=True,
        icon="mdi:signal-variant",
        native_unit_of_measurement="dBm",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda hub: get_first_int(
            hub.cellular_status,
            ("rsrp",),
            nested=("modem", "cellular", "sim", "signal"),
        ),
    ),
    HubSensorEntityDescription(
        key="cellular_rsrq",
        name="Cellular RSRQ",
        has_entity_name=True,
        icon="mdi:signal-distance-variant",
        native_unit_of_measurement="dB",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda hub: get_first_int(
            hub.cellular_status,
            ("rsrq",),
            nested=("modem", "cellular", "sim", "signal"),
        ),
    ),
    HubSensorEntityDescription(
        key="cellular_sinr",
        name="Cellular SINR",
        has_entity_name=True,
        icon="mdi:signal-3g",
        native_unit_of_measurement="dB",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda hub: get_first_int(
            hub.cellular_status,
            ("sinr",),
            nested=("modem", "cellular", "sim", "signal"),
        ),
    ),
    HubSensorEntityDescription(
        key="cellular_band",
        name="Cellular band",
        has_entity_name=True,
        icon="mdi:cellphone-wireless",
        value_fn=lambda hub: get_first_value(
            hub.cellular_status,
            ("band", "network_type", "service_type"),
            nested=("modem", "cellular", "sim"),
        ),
    ),
    HubSensorEntityDescription(
        key="cellular_network",
        name="Cellular network",
        has_entity_name=True,
        icon="mdi:signal-cellular-outline",
        value_fn=lambda hub: get_first_value(
            hub.cellular_status,
            ("network", "operator", "operator_name", "carrier", "mode", "service_type"),
            nested=("modem", "cellular", "sim"),
        ),
    ),
    HubSensorEntityDescription(
        key="sms_messages",
        name="Text messages",
        has_entity_name=True,
        icon="mdi:message-text",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda hub: len(hub.sms_messages),
        extra_attributes_fn=lambda hub: {
            "message_count": len(hub.sms_messages),
            "incoming_count": sum(
                1 for m in hub.sms_messages.values() if m.direction == "incoming"
            ),
            "outgoing_count": sum(
                1 for m in hub.sms_messages.values() if m.direction == "outgoing"
            ),
            "messages": [
                {
                    "id": message_id,
                    "phone_number": message.phone_number,
                    "direction": message.direction,
                    "status": message.status_label,
                    "timestamp": message.timestamp,
                    "text": message.text,
                }
                for message_id, message in hub.sms_messages.items()
            ],
        },
    ),
    HubSensorEntityDescription(
        key="repeater_state",
        name="Repeater state",
        has_entity_name=True,
        icon="mdi:wifi-sync",
        device_class=SensorDeviceClass.ENUM,
        options=["not_used", "connecting", "connected", "failed"],
        value_fn=lambda hub: _repeater_state_value(hub),
        extra_attributes_fn=lambda hub: _repeater_state_attributes(hub),
    ),
    HubSensorEntityDescription(
        key="repeater_ssid",
        name="Repeater SSID",
        has_entity_name=True,
        icon="mdi:wifi",
        value_fn=lambda hub: hub.repeater_status.ssid if hub.repeater_status else None,
    ),
    HubSensorEntityDescription(
        key="repeater_signal",
        name="Repeater signal",
        has_entity_name=True,
        icon="mdi:wifi-strength-2",
        native_unit_of_measurement="dBm",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda hub: hub.repeater_status.signal if hub.repeater_status else None,
    ),
    HubSensorEntityDescription(
        key="repeater_ip",
        name="Repeater IP address",
        has_entity_name=True,
        icon="mdi:ip-network",
        value_fn=lambda hub: hub.repeater_status.ipv4_address if hub.repeater_status else None,
    ),
    HubSensorEntityDescription(
        key="repeater_gateway",
        name="Repeater gateway",
        has_entity_name=True,
        icon="mdi:router-network",
        value_fn=lambda hub: hub.repeater_status.ipv4_gateway if hub.repeater_status else None,
    ),
    HubSensorEntityDescription(
        key="repeater_dns",
        name="Repeater DNS",
        has_entity_name=True,
        icon="mdi:dns",
        value_fn=lambda hub: (
            hub.repeater_status.ipv4_dns[0]
            if hub.repeater_status and hub.repeater_status.ipv4_dns
            else None
        ),
        extra_attributes_fn=lambda hub: (
            {"dns_servers": hub.repeater_status.ipv4_dns}
            if hub.repeater_status and hub.repeater_status.ipv4_dns
            else None
        ),
    ),
    HubSensorEntityDescription(
        key="repeater_bssid",
        name="Repeater BSSID",
        has_entity_name=True,
        icon="mdi:access-point-network",
        value_fn=lambda hub: hub.repeater_status.bssid if hub.repeater_status else None,
    ),
)

FEATURE_SENSOR_MAP: dict[str, str] = {
    "cellular_signal": FEATURE_CELLULAR,
    "cellular_rssi": FEATURE_CELLULAR,
    "cellular_rsrp": FEATURE_CELLULAR,
    "cellular_rsrq": FEATURE_CELLULAR,
    "cellular_sinr": FEATURE_CELLULAR,
    "cellular_band": FEATURE_CELLULAR,
    "cellular_network": FEATURE_CELLULAR,
    "sms_messages": FEATURE_SMS,
    "repeater_state": FEATURE_REPEATER,
    "repeater_ssid": FEATURE_REPEATER,
    "repeater_signal": FEATURE_REPEATER,
    "repeater_ip": FEATURE_REPEATER,
    "repeater_gateway": FEATURE_REPEATER,
    "repeater_dns": FEATURE_REPEATER,
    "repeater_bssid": FEATURE_REPEATER,
}


def _sensor_is_enabled(hub: GLinetHub, description: HubSensorEntityDescription) -> bool:
    feature = FEATURE_SENSOR_MAP.get(description.key)
    return feature is None or hub.feature_enabled(feature)


@dataclass(frozen=True, kw_only=True)
class ClientBandwidthEntityDescription(SensorEntityDescription):
    value_fn: Callable[[ClientDeviceInfo], int | None]


CLIENT_BANDWIDTH_SENSORS: tuple[ClientBandwidthEntityDescription, ...] = (
    ClientBandwidthEntityDescription(
        key="rx_rate",
        name="Download rate",
        icon="mdi:download-network",
        device_class=SensorDeviceClass.DATA_RATE,
        native_unit_of_measurement="B/s",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.rx_rate,
    ),
    ClientBandwidthEntityDescription(
        key="tx_rate",
        name="Upload rate",
        icon="mdi:upload-network",
        device_class=SensorDeviceClass.DATA_RATE,
        native_unit_of_measurement="B/s",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.tx_rate,
    ),
)


def _repeater_state_value(hub: GLinetHub) -> str | None:
    if hub.repeater_status is None:
        return None
    state_map = {
        RepeaterState.NOT_USED: "not_used",
        RepeaterState.CONNECTING: "connecting",
        RepeaterState.CONNECTED: "connected",
        RepeaterState.FAILED: "failed",
    }
    return state_map.get(hub.repeater_status.state)


def _repeater_state_attributes(hub: GLinetHub) -> dict[str, Any] | None:
    if hub.repeater_status is None:
        return None
    attrs: dict[str, Any] = {}
    if hub.repeater_status.bssid:
        attrs["bssid"] = hub.repeater_status.bssid
    if hub.repeater_status.fail_type:
        attrs["fail_type"] = hub.repeater_status.fail_type
    return attrs if attrs else None


def _calc_usage_percent(total: Any, free: Any) -> float | None:
    if not isinstance(total, (int, float)) or total <= 0:
        return None
    if not isinstance(free, (int, float)) or free < 0:
        return None
    value = 100 * (1 - free / total)
    return value if 0 <= value <= 100 else None


def _resolve_uptime(seconds_uptime: float, last_value: datetime | None) -> datetime:
    delta_uptime = utcnow() - timedelta(seconds=seconds_uptime)
    if not last_value or abs((delta_uptime - last_value).total_seconds()) > 15:
        return delta_uptime
    return last_value


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    hub: GLinetHub = entry.runtime_data
    tracked: set[str] = set()
    entities: list[SensorEntity] = [
        SystemStatusSensor(hub=hub, entity_description=description)
        for description in SYSTEM_SENSORS
        if description.value_fn(hub.router_status) is not None
    ]
    entities.extend(
        HubStatusSensor(hub=hub, entity_description=description)
        for description in HUB_SENSORS
        if _sensor_is_enabled(hub, description)
    )
    entities.append(
        SystemUptimeSensor(
            hub=hub,
            entity_description=SystemStatusEntityDescription(
                key="uptime",
                name="Uptime",
                has_entity_name=True,
                icon="mdi:clock",
                entity_category=EntityCategory.DIAGNOSTIC,
                device_class=SensorDeviceClass.TIMESTAMP,
                value_fn=lambda _: None,
            ),
        )
    )
    if hub.feature_enabled(FEATURE_REPEATER):
        entities.append(RepeaterChannelSensor(hub=hub))

    async_add_entities(entities, True)

    @callback
    def register_client_bandwidth_sensors() -> None:
        new_entities: list[SensorEntity] = []
        for mac, device in hub.tracked_devices.items():
            for description in CLIENT_BANDWIDTH_SENSORS:
                unique_id = f"glinet_client_sensor/{mac}/{description.key}"
                if unique_id in tracked:
                    continue
                tracked.add(unique_id)
                new_entities.append(ClientBandwidthSensor(hub, device, description))
        if new_entities:
            async_add_entities(new_entities)

    register_client_bandwidth_sensors()
    entry.async_on_unload(
        async_dispatcher_connect(
            hub.hass,
            hub.event_device_added,
            register_client_bandwidth_sensors,
        )
    )


class GLinetSensorBase(SensorEntity):
    def __init__(self, hub: GLinetHub, entity_description: SystemStatusEntityDescription) -> None:
        self.hub = hub
        self.entity_description = entity_description
        self._attr_device_info = hub.device_info

    @property
    def unique_id(self) -> str:
        return f"glinet_sensor/{self.hub.device_mac}/system_{self.entity_description.key}"

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        if self.entity_description.extra_attributes_fn is None:
            return None
        return self.entity_description.extra_attributes_fn(self.hub.router_status)


class SystemStatusSensor(GLinetSensorBase):
    @property
    def native_value(self) -> int | float | None:
        return self.entity_description.value_fn(self.hub.router_status)


class HubStatusSensor(SensorEntity):
    def __init__(self, hub: GLinetHub, entity_description: HubSensorEntityDescription) -> None:
        self.hub = hub
        self.entity_description = entity_description
        self._attr_device_info = hub.device_info

    @property
    def unique_id(self) -> str:
        return f"glinet_sensor/{self.hub.device_mac}/{self.entity_description.key}"

    @property
    def native_value(self) -> int | float | str | None:
        return self.entity_description.value_fn(self.hub)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        if self.entity_description.extra_attributes_fn is None:
            return None
        return self.entity_description.extra_attributes_fn(self.hub)


class SystemUptimeSensor(GLinetSensorBase):
    _current_value: datetime | None = None

    @property
    def native_value(self) -> datetime | None:
        uptime = self.hub.router_status.get("uptime")
        if not isinstance(uptime, (int, float)):
            return None
        self._current_value = _resolve_uptime(float(uptime), self._current_value)
        return self._current_value


class ClientBandwidthSensor(SensorEntity):
    _attr_has_entity_name = True

    def __init__(
        self,
        hub: GLinetHub,
        device: ClientDeviceInfo,
        entity_description: ClientBandwidthEntityDescription,
    ) -> None:
        self._hub = hub
        self._device = device
        self.entity_description = entity_description
        self._attr_device_info = DeviceInfo(
            connections={(CONNECTION_NETWORK_MAC, format_mac(device.mac))},
            name=device.name or device.mac,
            via_device=(DOMAIN, self._hub.router_id),
        )

    @property
    def unique_id(self) -> str:
        return f"glinet_client_sensor/{self._device.mac}/{self.entity_description.key}"

    @property
    def native_value(self) -> int | None:
        self._device = self._hub.tracked_devices.get(self._device.mac, self._device)
        return self.entity_description.value_fn(self._device)


class RepeaterChannelSensor(SensorEntity):
    """Sensor for repeater WiFi channel showing band and channel."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:radio-tower"
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = ["2_4ghz", "5ghz"]
    _attr_translation_key = "repeater_channel"

    def __init__(self, hub: GLinetHub) -> None:
        self._hub = hub
        self._attr_device_info = hub.device_info

    @property
    def unique_id(self) -> str:
        return f"glinet_sensor/{self._hub.device_mac}/repeater_channel"

    @property
    def native_value(self) -> str | None:
        if not self._hub.repeater_status:
            return None
        channel = self._hub.repeater_status.channel
        if channel is None:
            return None
        return channel_to_band(channel)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        if not self._hub.repeater_status:
            return None
        channel = self._hub.repeater_status.channel
        return {"channel": channel, "band": channel_to_band(channel)}
