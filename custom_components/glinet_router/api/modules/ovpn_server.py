from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .base import BaseModule

if TYPE_CHECKING:
    pass

class OvpnServerModule(BaseModule):
    async def get_status(self) -> dict[str, Any]:
        response = await self._call("ovpn-server", "get_status")
        return dict(response)

    async def start(self) -> dict[str, Any]:
        response = await self._call("ovpn-server", "start")
        return dict(response)

    async def stop(self) -> dict[str, Any]:
        response = await self._call("ovpn-server", "stop")
        return dict(response)

    async def get_config(self) -> dict[str, Any]:
        response = await self._call("ovpn-server", "get_config")
        return dict(response)

    async def get_user_list(self) -> list[dict[str, Any]]:
        response = await self._call("ovpn-server", "get_user_list")
        return [dict(item) for item in dict(response).get("user_list", [])]
