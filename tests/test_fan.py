from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from custom_components.ha_glinet.api.exceptions import NonZeroResponse
from custom_components.ha_glinet.hub import GLinetHub


@pytest.fixture
def mock_api():
    api = AsyncMock()
    api.fan = AsyncMock()
    return api

@pytest.fixture
def mock_hub(mock_api):
    entry = AsyncMock()
    entry.options = {}
    entry.data = {"host": "http://192.168.8.1", "password": "pass"}
    entry.entry_id = "test_entry"
    entry.runtime_data = None
    
    hub = GLinetHub(AsyncMock(), entry)
    hub._api = mock_api
    return hub

async def test_fetch_fan_status_success(mock_hub, mock_api):
    mock_api.fan.get_status = AsyncMock(return_value={"status": True, "speed": 1000})
    mock_api.fan.get_config = AsyncMock(return_value={"temperature": 75, "warn_temperature": 90})
    
    await mock_hub.fetch_fan_status()
    
    assert mock_hub.fan_running is True
    assert mock_hub.fan_speed == 1000
    assert mock_hub.fan_temperature_threshold == 75

async def test_fetch_fan_status_no_fan(mock_hub, mock_api):
    # Simulate "method not found" error
    mock_api.fan.get_status = AsyncMock(side_effect=NonZeroResponse("Method not found"))
    
    # Should not raise exception because of _invoke_optional_api fix
    await mock_hub.fetch_fan_status()
    
    assert mock_hub.fan_status is None
    assert mock_hub.fan_running is None

async def test_set_fan_temperature(mock_hub, mock_api):
    mock_api.fan.set_config = AsyncMock(return_value={})
    mock_api.fan.get_status = AsyncMock(return_value={"status": False, "speed": 0})
    mock_api.fan.get_config = AsyncMock(return_value={"temperature": 70})
    
    await mock_hub.set_fan_temperature(70)
    
    mock_api.fan.set_config.assert_called_once_with(70)
    assert mock_hub.fan_temperature_threshold == 70
