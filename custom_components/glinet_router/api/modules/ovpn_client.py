from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .base import BaseModule
from .vpn_client import VpnClientModule

if TYPE_CHECKING:
    from ..client import GLinetApiClient


class OvpnModule(BaseModule):
    async def get_all_config_list(self) -> dict[str, Any]:
        response = await self._call("ovpn-client", "get_all_config_list")
        return dict(response)

    async def get_group_list(self) -> dict[str, Any]:
        response = await self._call("ovpn-client", "get_group_list")
        return dict(response)

    async def get_config_list(self, group_id: int) -> dict[str, Any]:
        response = await self._call("ovpn-client", "get_config_list", {"group_id": group_id})
        return dict(response)


class OvpnClientModule(BaseModule):

    def __init__(self, client: GLinetApiClient) -> None:
        super().__init__(client)
        self.ovpn_legacy = OvpnModule(client)
        self.vpn_client = VpnClientModule(client)

    async def get_ovpn_clients(self) -> list[dict[str, Any]]:
        configs: list[dict[str, Any]] = []
        
        groups_response = await self.ovpn_legacy.get_group_list()
        groups = dict(groups_response).get("groups", [])
        
        for group in groups:
            group_id = group.get("group_id")
            group_name = group.get("group_name")
            
            clients_response = await self.ovpn_legacy.get_config_list(group_id)
            clients = dict(clients_response).get("clients", [])
            
            for client in clients:
                configs.append(
                    {
                        "name": client.get("name"),
                        "group_name": group_name,
                        "group_id": group_id,
                        "client_id": client.get("client_id"),
                        "location": client.get("location"),
                        "remote": client.get("remote"),
                        "type": "ovpn",
                        "raw_data": client,
                    }
                )
        
        tunnels_response = await self.vpn_client.get_tunnel()
        tunnels = dict(tunnels_response).get("tunnels", [])
        
        ovpn_tunnel_id = None
        for tunnel in tunnels:
            if tunnel.get("via", {}).get("type") == "openvpn":
                ovpn_tunnel_id = tunnel.get("tunnel_id")
                break
        
        if ovpn_tunnel_id is None:
             for tunnel in tunnels:
                 if tunnel.get("name") == "Primary Tunnel":
                     ovpn_tunnel_id = tunnel.get("tunnel_id")
                     break

        for config in configs:
            config["tunnel_id"] = ovpn_tunnel_id
            
        return configs

    async def get_status(self) -> list[dict[str, Any]]:
        response = await self.vpn_client.get_status()
        return [dict(item) for item in dict(response).get("status_list", [])]

    async def start(
        self, group_id: int, client_id: int, tunnel_id: int | None = None
    ) -> dict[str, Any]:
        if tunnel_id is None:
            tunnels = await self.vpn_client.get_tunnel()
            for tunnel in dict(tunnels).get("tunnels", []):
                if tunnel.get("via", {}).get("type") == "openvpn":
                    tunnel_id = tunnel.get("tunnel_id")
                    break
        
        if tunnel_id is None:
             raise ValueError("No OpenVPN tunnel found to start connection")
            
        return await self.vpn_client.set_tunnel(
            tunnel_id,
            True,
            via={"group_id": group_id, "client_id": client_id, "type": "openvpn"},
        )

    async def stop(
        self, group_id: int, client_id: int, tunnel_id: int | None = None
    ) -> dict[str, Any]:
        if tunnel_id is None:
             # Just find any active openvpn tunnel to stop it
             status = await self.get_status()
             for state in status:
                 if state.get("type") == "openvpn" and state.get("status") == 1:
                     tunnel_id = state.get("tunnel_id")
                     break
        
        if tunnel_id is None:
             return {"ok": True} # Already stopped
             
        return await self.vpn_client.set_tunnel(tunnel_id, False)
