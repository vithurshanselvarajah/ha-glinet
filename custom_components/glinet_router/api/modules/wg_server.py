from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .base import BaseModule

if TYPE_CHECKING:
    pass

class WgServerModule(BaseModule):

    async def get_status(self) -> dict[str, Any]:
        response = await self._call("wg-server", "get_status")
        return dict(response)

    async def start(self) -> dict[str, Any]:
        response = await self._call("wg-server", "start")
        return dict(response)

    async def stop(self) -> dict[str, Any]:
        response = await self._call("wg-server", "stop")
        return dict(response)

    async def get_config(self) -> dict[str, Any]:
        response = await self._call("wg-server", "get_config")
        return dict(response)

    async def set_config(
        self,
        address_v4: str,
        port: int,
        address_v6: str | None = None,
        private_key: str | None = None,
    ) -> dict[str, Any]:
        params = {
            "address_v4": address_v4,
            "port": port,
        }
        if address_v6:
            params["address_v6"] = address_v6
        if private_key:
            params["private_key"] = private_key
        response = await self._call("wg-server", "set_config", params)
        return dict(response)

    async def get_peer_list(self) -> list[dict[str, Any]]:
        response = await self._call("wg-server", "get_peer_list")
        return [dict(item) for item in dict(response).get("peers", [])]

    async def add_peer(self, name: str, **kwargs: Any) -> dict[str, Any]:
        params = {"name": name, **kwargs}
        response = await self._call("wg-server", "add_peer", params)
        return dict(response)

    async def remove_peer(self, peer_id: int, remove_all: bool = False) -> dict[str, Any]:
        params = {"peer_id": peer_id, "all": remove_all}
        response = await self._call("wg-server", "remove_peer", params)
        return dict(response)

    async def set_peer(self, peer_id: int, **kwargs: Any) -> dict[str, Any]:
        params = {"peer_id": peer_id, **kwargs}
        response = await self._call("wg-server", "set_peer", params)
        return dict(response)
