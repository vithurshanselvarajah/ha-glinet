from typing import Any

import pytest

from custom_components.ha_glinet.api.client import GLinetApiClient
from tests.test_api_client import FakeSession


@pytest.fixture
def ovpn_client_config_response() -> dict[str, Any]:
    return {
        "result": {
            "config_list": [
                {
                    "group_id": 1,
                    "group_name": "Provider1",
                    "clients": [
                        {
                            "client_id": 10,
                            "name": "Location1",
                            "location": "City1; City2",
                            "remote": ["remote1.com", "remote2.com"]
                        }
                    ]
                }
            ]
        }
    }

@pytest.fixture
def ovpn_client_status_response() -> dict[str, Any]:
    return {
        "result": {
            "status": 1,
            "group_id": 1,
            "client_id": 10,
            "domain": "remote1.com"
        }
    }

@pytest.fixture
def ovpn_server_status_response() -> dict[str, Any]:
    return {
        "result": {
            "status": 1,
            "initialization": True,
            "tunnel_ip": "10.8.0.1",
            "rx_bytes": 500,
            "tx_bytes": 600
        }
    }

async def test_ovpn_client_get_clients(ovpn_client_config_response: dict[str, Any]) -> None:
    session = FakeSession([ovpn_client_config_response])
    client = GLinetApiClient("http://router/rpc", session, sid="sid-1")
    
    clients = await client.ovpn_client.get_ovpn_clients()
    assert len(clients) == 1
    assert clients[0]["name"] == "Location1"
    assert clients[0]["group_name"] == "Provider1"
    assert clients[0]["location"] == "City1; City2"

async def test_ovpn_client_start() -> None:
    session = FakeSession([{"result": {"ok": True}}])
    client = GLinetApiClient("http://router/rpc", session, sid="sid-1")
    
    await client.ovpn_client.start(1, 10)
    expected_params = ["sid-1", "ovpn-client", "start", {"group_id": 1, "client_id": 10}]
    assert session.requests[0]["json"]["params"] == expected_params

async def test_ovpn_server_get_status(ovpn_server_status_response: dict[str, Any]) -> None:
    session = FakeSession([ovpn_server_status_response, {"result": {"user_list": []}}])
    client = GLinetApiClient("http://router/rpc", session, sid="sid-1")
    
    status = await client.ovpn_server.get_status()
    assert status["status"] == 1
    assert status["tunnel_ip"] == "10.8.0.1"

async def test_ovpn_client_set_config() -> None:
    session = FakeSession([{"result": {"ok": True}}])
    client = GLinetApiClient("http://router/rpc", session, sid="sid-1")
    
    await client.ovpn_client.set_config(
        {"group_id": 1, "client_id": 10, "remote": "new-remote.com"}
    )
    expected_params = [
        "sid-1",
        "ovpn-client",
        "set_config",
        {"group_id": 1, "client_id": 10, "remote": "new-remote.com"},
    ]
    assert session.requests[0]["json"]["params"] == expected_params
