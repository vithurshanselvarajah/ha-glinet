from typing import Any

import pytest

from custom_components.glinet_router.api.client import GLinetApiClient
from custom_components.glinet_router.api.const import FIRMWARE_4_8, FIRMWARE_4_9
from tests.test_api_client import FakeSession


def _make_client(responses: list[Any], version: tuple[int, int, int, int]) -> GLinetApiClient:
    session = FakeSession(responses)
    client = GLinetApiClient("http://router/rpc", session, sid="sid-1")
    client._firmware_version = version
    return client


async def test_set_tunnel_by_peer_emits_4_9_payload() -> None:
    client = _make_client([{"result": []}], FIRMWARE_4_9)

    await client.wg_client.vpn_client.set_tunnel_by_peer(
        enabled=True,
        tunnel_type="wireguard",
        group_id=1543,
        peer_id=2001,
    )

    assert client._session.requests[0]["json"]["params"] == [
        "sid-1",
        "vpn-client",
        "set_tunnel",
        {
            "enabled": True,
            "type": "wireguard",
            "group_id": 1543,
            "peer_id": 2001,
        },
    ]


async def test_set_tunnel_by_peer_includes_tunnel_id_when_provided() -> None:
    client = _make_client([{"result": []}], FIRMWARE_4_9)

    await client.wg_client.vpn_client.set_tunnel_by_peer(
        enabled=False,
        tunnel_type="wireguard",
        group_id=1543,
        peer_id=2001,
        tunnel_id=8040,
    )

    assert client._session.requests[0]["json"]["params"] == [
        "sid-1",
        "vpn-client",
        "set_tunnel",
        {
            "enabled": False,
            "type": "wireguard",
            "group_id": 1543,
            "peer_id": 2001,
            "tunnel_id": 8040,
        },
    ]


async def test_start_wireguard_client_uses_peer_payload_on_4_9() -> None:
    client = _make_client([{"result": []}], FIRMWARE_4_9)

    await client.wg_client.start_wireguard_client(group_id=1543, peer_id=2001)

    assert client._session.requests[0]["json"]["params"] == [
        "sid-1",
        "vpn-client",
        "set_tunnel",
        {
            "enabled": True,
            "type": "wireguard",
            "group_id": 1543,
            "peer_id": 2001,
        },
    ]


async def test_stop_wireguard_client_uses_peer_payload_on_4_9() -> None:
    client = _make_client([{"result": []}], FIRMWARE_4_9)

    await client.wg_client.stop_wireguard_client(group_id=1543, peer_id=2001)

    assert client._session.requests[0]["json"]["params"] == [
        "sid-1",
        "vpn-client",
        "set_tunnel",
        {
            "enabled": False,
            "type": "wireguard",
            "group_id": 1543,
            "peer_id": 2001,
        },
    ]


async def test_start_wireguard_client_uses_set_tunnel_on_4_8() -> None:
    client = _make_client([{"result": {"ok": True}}], FIRMWARE_4_8)

    await client.wg_client.start_wireguard_client(group_id=1543, peer_id=2001)

    assert client._session.requests[0]["json"]["params"] == [
        "sid-1",
        "vpn-client",
        "set_tunnel",
        {"enabled": True, "tunnel_id": 2001},
    ]


async def test_stop_wireguard_client_uses_set_tunnel_on_4_8() -> None:
    client = _make_client([{"result": {"ok": True}}], FIRMWARE_4_8)

    await client.wg_client.stop_wireguard_client(group_id=1543, peer_id=2001)

    assert client._session.requests[0]["json"]["params"] == [
        "sid-1",
        "vpn-client",
        "set_tunnel",
        {"enabled": False, "tunnel_id": 2001},
    ]


@pytest.mark.parametrize("future_version", [(4, 10, 0, 0), (5, 0, 0, 0), (5, 1, 3, 0)])
async def test_future_versions_keep_using_4_9_peer_payload(
    future_version: tuple[int, int, int, int],
) -> None:
    client = _make_client([{"result": []}], future_version)

    await client.wg_client.start_wireguard_client(group_id=1543, peer_id=2001)

    assert client._session.requests[0]["json"]["params"] == [
        "sid-1",
        "vpn-client",
        "set_tunnel",
        {
            "enabled": True,
            "type": "wireguard",
            "group_id": 1543,
            "peer_id": 2001,
        },
    ]
