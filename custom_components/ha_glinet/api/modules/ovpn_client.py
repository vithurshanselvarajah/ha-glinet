from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .base import BaseModule

if TYPE_CHECKING:
    pass

class OvpnClientModule(BaseModule):
    async def get_all_config_list(self) -> dict[str, Any]:
        response = await self._call("ovpn-client", "get_all_config_list")
        return dict(response)

    async def get_status(self) -> dict[str, Any]:
        response = await self._call("ovpn-client", "get_status")
        return dict(response)

    async def start(self, group_id: int, client_id: int) -> dict[str, Any]:
        response = await self._call(
            "ovpn-client", "start", {"group_id": group_id, "client_id": client_id}
        )
        return dict(response)

    async def stop(self) -> dict[str, Any]:
        response = await self._call("ovpn-client", "stop")
        return dict(response)

    async def set_config(self, params: dict[str, Any]) -> dict[str, Any]:
        response = await self._call("ovpn-client", "set_config", params)
        return dict(response)

    async def get_ovpn_clients(self) -> list[dict[str, Any]]:
        response = await self.get_all_config_list()
        configs: list[dict[str, Any]] = []
        for item in dict(response).get("config_list", []):
            clients = item.get("clients", [])
            if not clients:
                continue
            for client in clients:
                configs.append(
                    {
                        "name": client["name"],
                        "group_name": item["group_name"],
                        "group_id": item["group_id"],
                        "client_id": client["client_id"],
                        "location": client.get("location"),
                        "remote": client.get("remote"),
                        "raw_data": client,
                    }
                )
        return configs
