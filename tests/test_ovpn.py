from typing import Any

import pytest

from custom_components.ha_glinet.api.client import GLinetApiClient
from tests.test_api_client import FakeSession


@pytest.fixture
def vpn_client_tunnel_response() -> dict[str, Any]:
    return {
        "result": {
            "tunnels": [
                {
                    "name": "Primary Tunnel",
                    "tunnel_id": 10,
                    "enabled": False,
                    "via": {
                        "type": "openvpn",
                        "client_id": 2034,
                        "group_id": 65395,
                        "via": "ovpnclient1"
                    }
                }
            ]
        }
    }


@pytest.fixture
def ovpn_groups_response() -> dict[str, Any]:
    return {
        "result": {
            "groups": [
                {"group_id": 65395, "group_name": "NordVPN"}
            ]
        }
    }


@pytest.fixture
def ovpn_config_list_response() -> dict[str, Any]:
    return {
        "result": {
            "clients": [
                {
                    "client_id": 2034,
                    "name": "gr69.nordvpn.com.udp",
                    "location": "Greece, Athens",
                    "remote": ["156.67.94.2:1194"]
                }
            ]
        }
    }


async def test_ovpn_client_get_clients(
    ovpn_groups_response: dict[str, Any],
    ovpn_config_list_response: dict[str, Any],
    vpn_client_tunnel_response: dict[str, Any]
) -> None:
    session = FakeSession([
        ovpn_groups_response,
        ovpn_config_list_response,
        vpn_client_tunnel_response
    ])
    client = GLinetApiClient("http://router/rpc", session, sid="sid-1")

    clients = await client.ovpn_client.get_ovpn_clients()
    assert len(clients) == 1
    assert clients[0]["name"] == "gr69.nordvpn.com.udp"
    assert clients[0]["group_id"] == 65395
    assert clients[0]["client_id"] == 2034
    assert clients[0]["location"] == "Greece, Athens"
    assert clients[0]["tunnel_id"] == 10


async def test_ovpn_client_start() -> None:
    session = FakeSession([{"result": {"ok": True}}])
    client = GLinetApiClient("http://router/rpc", session, sid="sid-1")

    await client.ovpn_client.start(65395, 2034, tunnel_id=10)
    
    # Check start call (should be set_tunnel)
    expected_params = [
        "sid-1", 
        "vpn-client", 
        "set_tunnel", 
        {
            "enabled": True, 
            "tunnel_id": 10,
            "via": {"group_id": 65395, "client_id": 2034, "type": "openvpn"}
        }
    ]
    assert session.requests[0]["json"]["params"] == expected_params


async def test_ovpn_client_stop() -> None:
    session = FakeSession([{"result": {"ok": True}}])
    client = GLinetApiClient("http://router/rpc", session, sid="sid-1")

    await client.ovpn_client.stop(65395, 2034, tunnel_id=10)
    
    # Check stop call (should be set_tunnel)
    expected_params = [
        "sid-1", 
        "vpn-client", 
        "set_tunnel", 
        {"enabled": False, "tunnel_id": 10}
    ]
    assert session.requests[0]["json"]["params"] == expected_params


async def test_ovpn_server_get_status() -> None:
    response = {
        "result": {
            "status": 1,
            "initialization": True,
            "tunnel_ip": "10.8.0.1",
            "rx_bytes": 500,
            "tx_bytes": 600
        }
    }
    session = FakeSession([response, {"result": {"user_list": []}}])
    client = GLinetApiClient("http://router/rpc", session, sid="sid-1")

    status = await client.ovpn_server.get_status()
    assert status["status"] == 1
    assert status["tunnel_ip"] == "10.8.0.1"
