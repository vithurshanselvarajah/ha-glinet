from typing import Any

import pytest

from custom_components.ha_glinet.api.client import GLinetApiClient
from tests.test_api_client import FakeSession


@pytest.fixture
def wg_server_status_response() -> dict[str, Any]:
    return {
        "result": {
            "server": {
                "status": 1,
                "initialization": True,
                "log": "",
                "tunnel_ip": "10.0.0.1/24",
                "rx_bytes": 1000,
                "tx_bytes": 2000
            },
            "peers": [
                {
                    "name": "peer1",
                    "status": 1,
                    "peer_id": 1
                },
                {
                    "name": "peer2",
                    "status": 0,
                    "peer_id": 2
                }
            ]
        }
    }

async def test_wg_server_get_status(wg_server_status_response: dict[str, Any]) -> None:
    session = FakeSession([wg_server_status_response])
    client = GLinetApiClient("http://router/rpc", session, sid="sid-1")
    
    status = await client.wg_server.get_status()
    assert status["server"]["status"] == 1
    assert len(status["peers"]) == 2
    assert session.requests[0]["json"]["params"] == ["sid-1", "wg-server", "get_status", {}]

async def test_wg_server_start() -> None:
    session = FakeSession([{"result": {"ok": True}}])
    client = GLinetApiClient("http://router/rpc", session, sid="sid-1")
    
    await client.wg_server.start()
    assert session.requests[0]["json"]["params"] == ["sid-1", "wg-server", "start", {}]

async def test_wg_server_stop() -> None:
    session = FakeSession([{"result": {"ok": True}}])
    client = GLinetApiClient("http://router/rpc", session, sid="sid-1")
    
    await client.wg_server.stop()
    assert session.requests[0]["json"]["params"] == ["sid-1", "wg-server", "stop", {}]

async def test_wg_server_get_peer_list() -> None:
    session = FakeSession([{"result": {"peers": [{"name": "p1"}]}}])
    client = GLinetApiClient("http://router/rpc", session, sid="sid-1")
    
    peers = await client.wg_server.get_peer_list()
    assert len(peers) == 1
    assert peers[0]["name"] == "p1"
    assert session.requests[0]["json"]["params"] == ["sid-1", "wg-server", "get_peer_list", {}]
