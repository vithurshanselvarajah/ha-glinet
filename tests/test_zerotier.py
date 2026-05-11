from typing import Any

import pytest

from custom_components.ha_glinet.api.client import GLinetApiClient
from tests.test_api_client import FakeSession


@pytest.fixture
def zerotier_config_response() -> dict[str, Any]:
    return {
        "result": {
            "id": "12345678",
            "enable": True,
            "lan_enabled": True,
            "wan_enabled": False
        }
    }

@pytest.fixture
def zerotier_status_response() -> dict[str, Any]:
    return {
        "result": {
            "status": 0,
            "zerotier_ip": "10.147.17.1",
            "lan_ip": "192.168.8.0/24",
            "wan_ip": "1.1.1.1"
        }
    }

async def test_zerotier_get_config(zerotier_config_response: dict[str, Any]) -> None:
    session = FakeSession([zerotier_config_response])
    client = GLinetApiClient("http://router/rpc", session, sid="sid-1")
    
    config = await client.zerotier.get_config()
    assert config["id"] == "12345678"
    assert config["enable"] is True

async def test_zerotier_get_status(zerotier_status_response: dict[str, Any]) -> None:
    session = FakeSession([zerotier_status_response])
    client = GLinetApiClient("http://router/rpc", session, sid="sid-1")
    
    status = await client.zerotier.get_status()
    assert status["status"] == 0
    assert status["zerotier_ip"] == "10.147.17.1"

async def test_zerotier_set_config() -> None:
    session = FakeSession([{"result": {"ok": True}}])
    client = GLinetApiClient("http://router/rpc", session, sid="sid-1")
    
    params = {"enabled": True, "id": "12345678"}
    await client.zerotier.set_config(params)
    expected_params = ["sid-1", "zerotier", "set_config", params]
    assert session.requests[0]["json"]["params"] == expected_params
