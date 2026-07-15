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


async def test_wg_vpn_client_exposes_get_tunnel() -> None:
    from custom_components.glinet_router.api.modules.wg_client import (
        VpnClientModule as WgVpnClientModule,
    )

    assert hasattr(WgVpnClientModule, "get_tunnel")
    assert hasattr(WgVpnClientModule, "get_status")
    assert hasattr(WgVpnClientModule, "set_tunnel")

    client = _make_client(
        [{"result": {"tunnels": [], "default_tunnels": []}}], FIRMWARE_4_9
    )
    response = await client.wg_client.vpn_client.get_tunnel()

    assert response == {"tunnels": [], "default_tunnels": []}
    assert client._session.requests[0]["json"]["params"] == [
        "sid-1",
        "vpn-client",
        "get_tunnel",
        {},
    ]


async def test_wg_vpn_client_get_tunnel_falls_back_on_legacy_firmware() -> None:
    from custom_components.glinet_router.api.exceptions import NonZeroResponse

    class _BoomSession(FakeSession):
        def __init__(self) -> None:
            super().__init__([])

        def post(self, url: str, json: dict[str, Any], timeout: int):  # type: ignore[override]
            from tests.test_api_client import FakePostContext, FakeResponse

            return FakePostContext(
                FakeResponse(
                    {
                        "jsonrpc": "2.0",
                        "error": {"code": -32001, "message": "unsupported"},
                    }
                )
            )

    session = _BoomSession()
    client = GLinetApiClient("http://router/rpc", session, sid="sid-1")
    client._firmware_version = FIRMWARE_4_8

    response = await client.wg_client.vpn_client.get_tunnel()

    assert response == {"tunnels": [], "default_tunnels": []}
    # The raised NonZeroResponse must not propagate to the caller.
    assert isinstance(
        NonZeroResponse.__mro__[0], type
    )  # keeps the import alive for static analysis
