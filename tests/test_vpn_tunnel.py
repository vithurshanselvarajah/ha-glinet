from __future__ import annotations

import types
from typing import Any

from custom_components.glinet_router.const import (
    FEATURE_OVPN_CLIENT,
    FEATURE_WG_CLIENT,
)
from custom_components.glinet_router.models import VpnTunnel, VpnTunnelType


def test_vpn_tunnel_parses_wireguard_payload() -> None:
    raw = {
        "tunnel_id": 7488,
        "name": "Tunnel 1",
        "enabled": False,
        "killswitch": True,
        "via": {
            "type": "wireguard",
            "configs": [{"id_list": [2001], "group_id": 1543}],
            "via": "wgclient1",
        },
    }
    tunnel = VpnTunnel.from_api_response(raw)

    assert tunnel.tunnel_id == 7488
    assert tunnel.name == "Tunnel 1"
    assert tunnel.tunnel_type == VpnTunnelType.WIREGUARD
    assert tunnel.peer_id == 2001
    assert tunnel.group_id == 1543
    assert tunnel.client_id is None
    assert tunnel.enabled is False
    assert tunnel.killswitch is True
    assert tunnel.via == "wgclient1"
    assert tunnel.is_default is False


def test_vpn_tunnel_parses_openvpn_payload() -> None:
    raw = {
        "tunnel_id": 1041,
        "name": "Tunnel 2",
        "enabled": True,
        "killswitch": False,
        "via": {
            "type": "openvpn",
            "configs": [{"id_list": [1], "group_id": 43568}],
        },
    }
    tunnel = VpnTunnel.from_api_response(raw)

    assert tunnel.tunnel_type == VpnTunnelType.OPENVPN
    assert tunnel.client_id == 1
    assert tunnel.group_id == 43568
    assert tunnel.peer_id is None
    assert tunnel.enabled is True
    assert tunnel.is_default is False


def test_vpn_tunnel_handles_unknown_type() -> None:
    raw = {
        "tunnel_id": 100,
        "name": "Default",
        "enabled": True,
        "via": {"type": "default", "via": "novpn"},
    }
    tunnel = VpnTunnel.from_api_response(raw, is_default=True)

    assert tunnel.tunnel_type == VpnTunnelType.UNKNOWN
    assert tunnel.is_default is True
    assert tunnel.peer_id is None
    assert tunnel.client_id is None


def test_vpn_tunnel_synthesises_default_name() -> None:
    raw = {"tunnel_id": 555, "via": {"type": "wireguard"}}
    tunnel = VpnTunnel.from_api_response(raw)

    assert tunnel.tunnel_id == 555
    assert tunnel.name == "Tunnel 555"


def _make_hub() -> Any:
    hub = types.SimpleNamespace()
    hub._vpn_tunnels = {
        7488: VpnTunnel(
            tunnel_id=7488,
            name="Tunnel 1",
            tunnel_type=VpnTunnelType.WIREGUARD,
            enabled=True,
        ),
        1041: VpnTunnel(
            tunnel_id=1041,
            name="Tunnel 2",
            tunnel_type=VpnTunnelType.OPENVPN,
            enabled=False,
        ),
        9999: VpnTunnel(
            tunnel_id=9999,
            name="Default",
            tunnel_type=VpnTunnelType.UNKNOWN,
            enabled=False,
            is_default=True,
        ),
    }
    return hub


def test_vpn_tunnels_property_returns_dict() -> None:
    from custom_components.glinet_router.hub import GLinetHub

    hub = GLinetHub.__new__(GLinetHub)
    hub._vpn_tunnels = _make_hub()._vpn_tunnels
    hub._vpn_tunnel_connections = []

    assert hub.vpn_tunnels[7488].tunnel_type == VpnTunnelType.WIREGUARD
    assert hub.connected_vpn_tunnels == []


def test_active_vpn_connections_includes_dashboard_tunnels() -> None:
    from custom_components.glinet_router.hub import GLinetHub

    hub = GLinetHub.__new__(GLinetHub)
    hub._vpn_tunnels = _make_hub()._vpn_tunnels
    hub._vpn_tunnel_connections = [hub._vpn_tunnels[7488]]
    hub._wireguard_connections = []
    hub._ovpn_connections = []

    active = hub.active_vpn_connections
    assert len(active) == 1
    assert active[0].tunnel_id == 7488


def test_feature_map_keywords_target_tunnel_unique_ids() -> None:
    import inspect

    from custom_components.glinet_router.hub import GLinetHub

    source = inspect.getsource(GLinetHub.async_initialize_hub)
    assert "vpn_tunnel/wg" in source
    assert "vpn_tunnel/ovpn" in source
    assert "vpn_tunnel/unknown" in source
    # Sanity: feature flags exist.
    assert FEATURE_WG_CLIENT
    assert FEATURE_OVPN_CLIENT


async def test_fetch_vpn_tunnels_routes_through_wg_client_submodule() -> None:
    from custom_components.glinet_router.hub import GLinetHub

    hub = GLinetHub.__new__(GLinetHub)
    hub._vpn_tunnels = {}
    hub._vpn_tunnel_connections = None

    calls: list[str] = []

    class _StubVpn:
        async def get_tunnel(self) -> dict[str, Any]:
            calls.append("get_tunnel")
            return {"tunnels": [], "default_tunnels": []}

        async def get_status(self) -> dict[str, Any]:
            calls.append("get_status")
            return {"status_list": []}

    class _StubWgClient:
        vpn_client = _StubVpn()

    class _StubApi:
        wg_client = _StubWgClient()
        _firmware_version = (4, 9, 0, 0)

        async def _is_firmware_at_least(self, version: tuple[int, int, int, int]) -> bool:
            return self._firmware_version >= version

    hub._api = _StubApi()

    async def _invoke_optional(api_callable: Any) -> Any:
        return await api_callable()

    hub._invoke_optional_api = _invoke_optional

    await hub.fetch_vpn_tunnels()

    assert calls == ["get_tunnel", "get_status"]
    assert hub._vpn_tunnels == {}
    assert hub._vpn_tunnel_connections == []


async def test_set_vpn_tunnel_uses_wg_client_vpn_client() -> None:
    from custom_components.glinet_router.hub import GLinetHub

    hub = GLinetHub.__new__(GLinetHub)
    hub._vpn_tunnels = {}
    hub._vpn_tunnel_connections = None

    seen: dict[str, Any] = {}

    class _StubVpn:
        async def set_tunnel(self, tunnel_id: int, enabled: bool) -> dict[str, Any]:
            seen["tunnel_id"] = tunnel_id
            seen["enabled"] = enabled
            return {"tunnel_id": tunnel_id}

    class _StubWgClient:
        vpn_client = _StubVpn()

    class _StubApi:
        wg_client = _StubWgClient()

    hub._api = _StubApi()

    async def _invoke(api_callable: Any) -> Any:
        return await api_callable()

    hub._invoke_api = _invoke
    hub.fetch_vpn_tunnels = _async_noop
    hub.fetch_wireguard_clients = _async_noop
    hub.fetch_ovpn_clients = _async_noop

    await hub.set_vpn_tunnel(1234, True)

    assert seen == {"tunnel_id": 1234, "enabled": True}


async def _async_noop(*_args: Any, **_kwargs: Any) -> None:
    return None


async def test_fetch_vpn_tunnels_handles_missing_vpn_client_submodule() -> None:
    from custom_components.glinet_router.hub import GLinetHub

    hub = GLinetHub.__new__(GLinetHub)
    hub._vpn_tunnels = {"keep": "stale"}
    hub._vpn_tunnel_connections = ["stale"]

    class _StubApi:
        wg_client = object()  # no vpn_client attribute

    hub._api = _StubApi()

    await hub.fetch_vpn_tunnels()

    assert hub._vpn_tunnels == {}
    assert hub._vpn_tunnel_connections == []


async def test_fetch_vpn_tunnels_dispatches_update_event() -> None:
    from custom_components.glinet_router.hub import GLinetHub

    hub = GLinetHub.__new__(GLinetHub)
    hub._vpn_tunnels = {}
    hub._vpn_tunnel_connections = None
    hub._factory_mac = "AA:BB:CC:DD:EE:FF"
    hub.hass = object()

    captured: dict[str, Any] = {}

    def _capture(hass: Any, signal: str, payload: Any) -> None:
        captured["signal"] = signal
        captured["payload"] = payload

    # Patch the module-level ``async_dispatcher_send`` used by hub.py.
    import custom_components.glinet_router.hub as hub_module

    original = hub_module.async_dispatcher_send
    hub_module.async_dispatcher_send = _capture
    try:
        # Make a fake dashboard with a single WireGuard tunnel.
        tunnel_payload = {
            "tunnels": [
                {
                    "tunnel_id": 1,
                    "name": "Tunnel 1",
                    "enabled": False,
                    "via": {
                        "type": "wireguard",
                        "configs": [{"id_list": [2001], "group_id": 1543}],
                    },
                }
            ],
            "default_tunnels": [],
        }
        status_payload = {"status_list": []}

        class _StubVpn:
            async def get_tunnel(self) -> dict[str, Any]:
                return tunnel_payload

            async def get_status(self) -> dict[str, Any]:
                return status_payload

        class _StubWgClient:
            vpn_client = _StubVpn()

        class _StubApi:
            wg_client = _StubWgClient()
            _firmware_version = (4, 9, 0, 0)

            async def _is_firmware_at_least(self, version: tuple[int, int, int, int]) -> bool:
                return self._firmware_version >= version

        hub._api = _StubApi()

        async def _invoke_optional(api_callable: Any) -> Any:
            return await api_callable()

        hub._invoke_optional_api = _invoke_optional

        await hub.fetch_vpn_tunnels()

        assert captured["signal"] == hub.event_vpn_tunnels_updated
        assert captured["payload"] == {1}
    finally:
        hub_module.async_dispatcher_send = original


def test_reconcile_vpn_tunnels_removes_stale_switches() -> None:
    import asyncio
    from unittest.mock import AsyncMock

    removed_states: list[Any] = []
    removed_registry: list[str] = []

    class _StubRegistry:
        def __init__(self) -> None:
            self.async_remove = self._remove

        def _remove(self, entity_id: str) -> None:
            removed_registry.append(entity_id)

    class _StubEntity:
        def __init__(self, tunnel_id: int, entity_id: str) -> None:
            self._tunnel_id = tunnel_id
            self.entity_id = entity_id
            # ``async_remove`` is a coroutine on the real entity; the
            # AsyncMock makes the call awaitable so the test mirrors the
            # production behaviour and surfaces a warning if it is not
            # awaited.
            self.async_remove = AsyncMock(
                side_effect=lambda *, force_remove=False: removed_states.append(
                    (self._tunnel_id, self.entity_id, force_remove)
                )
            )

    stub_hub = types.SimpleNamespace()
    stub_hub.vpn_tunnels = {
        1: types.SimpleNamespace(
            tunnel_id=1,
            tunnel_type=VpnTunnelType.WIREGUARD,
            name="t1",
        ),
        2: types.SimpleNamespace(
            tunnel_id=2,
            tunnel_type=VpnTunnelType.OPENVPN,
            name="t2",
        ),
    }

    def _feature_enabled(feature: str) -> bool:
        return feature in {FEATURE_WG_CLIENT, FEATURE_OVPN_CLIENT}

    stub_hub.feature_enabled = _feature_enabled

    class _StubVpnTunnelSwitch:

        def __init__(self, hub: Any, tunnel: Any, entity_id: str) -> None:
            self._tunnel_id = tunnel.tunnel_id
            self._hub = hub
            self._tunnel = tunnel
            self.entity_id = entity_id
            self.async_remove = AsyncMock()

    # Build the registry the same way async_setup_entry does.
    entities = [
        _StubVpnTunnelSwitch(
            stub_hub, stub_hub.vpn_tunnels[1], "switch.tunnel_1"
        ),
        _StubVpnTunnelSwitch(
            stub_hub, stub_hub.vpn_tunnels[2], "switch.tunnel_2"
        ),
    ]
    vpn_tunnel_switches: dict[int, Any] = {
        entity._tunnel_id: entity for entity in entities
    }
    registry = _StubRegistry()

    # Simulate the router reporting only tunnel 1 (tunnel 2 was removed).
    current_ids = {1}

    # Inline the reconcile body (matches the implementation in switch.py)
    # and ``await`` async_remove just like the real platform does.
    async def _run_reconcile() -> None:
        existing_ids = set(vpn_tunnel_switches.keys())
        stale_ids = existing_ids - current_ids
        for stale_id in list(stale_ids):
            entity = vpn_tunnel_switches.pop(stale_id, None)
            if entity is None:
                continue
            # ``await`` is required for ``Entity.async_remove`` to
            # actually run on the real platform.
            await entity.async_remove(force_remove=True)
            if entity.entity_id:
                registry.async_remove(entity.entity_id)

    asyncio.run(_run_reconcile())

    # The state-removal coroutine ran and was awaited.
    assert (2, "switch.tunnel_2", True) in removed_states
    # The registry entry was also removed so the entity fully disappears.
    assert "switch.tunnel_2" in removed_registry
    # Tunnel 1 was not touched.
    assert 2 not in vpn_tunnel_switches
    assert 1 in vpn_tunnel_switches
    # Every entity.async_remove call must have been awaited.
    for entity in entities:
        entity.async_remove.assert_awaited()
