from typing import Any

import pytest

from custom_components.ha_glinet.api.client import GLinetApiClient
from tests.test_api_client import FakeSession


@pytest.fixture
def led_config_response() -> dict[str, Any]:
    return {
        "result": {
            "led_enable": True
        }
    }

async def test_led_get_config(led_config_response: dict[str, Any]) -> None:
    session = FakeSession([led_config_response])
    client = GLinetApiClient("http://router/rpc", session, sid="sid-1")
    
    config = await client.led.get_config()
    assert config["led_enable"] is True

async def test_led_set_config() -> None:
    session = FakeSession([{"result": None}])
    client = GLinetApiClient("http://router/rpc", session, sid="sid-1")
    
    await client.led.set_config({"led_enable": False})
    expected_params = ["sid-1", "led", "set_config", {"led_enable": False}]
    assert session.requests[0]["json"]["params"] == expected_params
