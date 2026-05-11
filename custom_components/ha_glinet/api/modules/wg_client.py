from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..const import NEW_VPN_CLIENT_VERSION
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

    async def start(self, group_id: int, peer_id: int) -> dict[str, Any]:
        response = await self._call(
            "wg-client", "start", {"group_id": group_id, "peer_id": peer_id}
        )
        return dict(response)

    async def stop(self) -> dict[str, Any]:
        response = await self._call("wg-client", "stop")
        return dict(response)

class VpnClientModule(BaseModule):
    async def get_status(self) -> dict[str, Any]:
        response = await self._call("vpn-client", "get_status")
        return dict(response)

    async def set_tunnel(self, tunnel_id: int, enabled: bool) -> dict[str, Any]:
        response = await self._call(
            "vpn-client", "set_tunnel", {"enabled": enabled, "tunnel_id": tunnel_id}
        )
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
        if self._client._firmware_version is None:
            await self._client.system.get_info()

        fw_ver = self._client._firmware_version
        if fw_ver is not None and fw_ver >= NEW_VPN_CLIENT_VERSION:
            response = await self.vpn_client.get_status()
            return [dict(item) for item in dict(response).get("status_list", [])]

        response = await self.wireguard.get_status()
        return [dict(response)]

    async def start_wireguard_client(self, group_id: int, peer_or_tunnel_id: int) -> dict[str, Any]:
        return await self._toggle_wireguard_client(group_id, peer_or_tunnel_id, True)

    async def stop_wireguard_client(self, peer_or_tunnel_id: int) -> dict[str, Any]:
        return await self._toggle_wireguard_client(-1, peer_or_tunnel_id, False)

    async def _toggle_wireguard_client(
        self, group_id: int, peer_or_tunnel_id: int, enabled: bool
    ) -> dict[str, Any]:
        if self._client._firmware_version is None:
            await self._client.system.get_info()

        fw_ver = self._client._firmware_version
        if fw_ver is not None and fw_ver >= NEW_VPN_CLIENT_VERSION:
            return await self.vpn_client.set_tunnel(peer_or_tunnel_id, enabled)

        if enabled:
            return await self.wireguard.start(group_id, peer_or_tunnel_id)

        return await self.wireguard.stop()
