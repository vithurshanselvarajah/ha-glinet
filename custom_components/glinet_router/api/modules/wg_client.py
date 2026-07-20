from __future__ import annotations

from typing import TYPE_CHECKING, Any

from aiohttp import ClientError

from ..const import FIRMWARE_4_9
from ..exceptions import APIClientError
from .base import BaseModule

if TYPE_CHECKING:
    from ..client import GLinetApiClient


class WireGuardModule(BaseModule):
    async def get_all_config_list(self) -> dict[str, Any]:
        response = await self._call("wg-client", "get_all_config_list")
        return dict(response)

    async def get_status(self) -> dict[str, Any]:
        response = await self._call("wg-client", "get_status")
        return dict(response)


class VpnClientModule(BaseModule):
    async def get_status(self) -> dict[str, Any]:
        response = await self._call("vpn-client", "get_status")
        return dict(response)

    async def get_tunnel(self) -> dict[str, Any]:
        try:
            response = await self._call("vpn-client", "get_tunnel")
        except (APIClientError, ClientError, TimeoutError, OSError):
            return {"tunnels": [], "default_tunnels": []}
        return dict(response)

    async def set_tunnel(self, tunnel_id: int, enabled: bool) -> dict[str, Any]:
        response = await self._call(
            "vpn-client", "set_tunnel", {"enabled": enabled, "tunnel_id": tunnel_id}
        )
        return dict(response)

    async def set_tunnel_by_peer(
        self,
        enabled: bool,
        tunnel_type: str,
        group_id: int | None = None,
        peer_id: int | None = None,
        tunnel_id: int | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"enabled": enabled, "type": tunnel_type}
        if group_id is not None:
            params["group_id"] = group_id
        if peer_id is not None:
            params["peer_id"] = peer_id
        if tunnel_id is not None:
            params["tunnel_id"] = tunnel_id
        response = await self._call("vpn-client", "set_tunnel", params)
        return dict(response)


class WgClientModule(BaseModule):
    def __init__(self, client: GLinetApiClient) -> None:
        super().__init__(client)
        self.wireguard = WireGuardModule(client)
        self.vpn_client = VpnClientModule(client)

    async def get_wireguard_clients(self) -> list[dict[str, Any]]:
        response = await self.wireguard.get_all_config_list()
        configs: list[dict[str, Any]] = []
        for item in dict(response).get("config_list", []):
            peers = item.get("peers", [])
            if not peers:
                continue
            for peer in peers:
                configs.append(
                    {
                        "name": f"{item['group_name']}/{peer['name']}",
                        "group_id": item["group_id"],
                        "peer_id": peer["peer_id"],
                        "tunnel_id": peer.get("tunnel_id"),
                    }
                )
        return configs

    async def get_wireguard_state(self) -> list[dict[str, Any]]:
        if await self._client._is_firmware_at_least(FIRMWARE_4_9):
            response = await self.vpn_client.get_status()
            return [dict(item) for item in dict(response).get("status_list", [])]

        response = await self.wireguard.get_status()
        return [dict(response)]

    async def start_wireguard_client(self, group_id: int, peer_id: int) -> dict[str, Any]:
        return await self._toggle_wireguard_client(group_id, peer_id, True)

    async def stop_wireguard_client(self, group_id: int, peer_id: int) -> dict[str, Any]:
        return await self._toggle_wireguard_client(group_id, peer_id, False)

    async def _toggle_wireguard_client(
        self, group_id: int, peer_id: int, enabled: bool
    ) -> dict[str, Any]:
        if await self._client._is_firmware_at_least(FIRMWARE_4_9):
            return await self.vpn_client.set_tunnel_by_peer(
                enabled=enabled,
                tunnel_type="wireguard",
                group_id=group_id,
                peer_id=peer_id,
            )

        return await self.vpn_client.set_tunnel(peer_id, enabled)
