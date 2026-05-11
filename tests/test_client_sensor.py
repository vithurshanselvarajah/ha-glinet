from unittest.mock import MagicMock

from homeassistant.const import EntityCategory

from custom_components.ha_glinet.entities.sensor import ClientSensor, ClientSensorEntityDescription
from custom_components.ha_glinet.models import ClientDeviceInfo


def test_client_ip_sensor() -> None:
    hub = MagicMock()
    hub.router_id = "test_router"
    hub.tracked_devices = {}
    
    device = ClientDeviceInfo("aa:bb:cc:dd:ee:ff", "Test Device")
    device.apply_update({"ip": "192.168.8.10", "online": True})
    
    description = ClientSensorEntityDescription(
        key="ip_address",
        name="IP address",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: d.ip_address,
    )
    
    sensor = ClientSensor(hub, device, description)
    
    assert sensor.native_value == "192.168.8.10"
    assert sensor.entity_category == EntityCategory.DIAGNOSTIC
    assert sensor.name == "IP address"
    assert sensor.unique_id == "glinet_client_sensor/aa:bb:cc:dd:ee:ff/ip_address"
