from __future__ import annotations

from typing import Any
from .base import BaseModule

class ClientsModule(BaseModule):
    async def get_list(self) -> dict[str, Any]:
        response = await self._call("clients", "get_list")
        return dict(response)

    async def get_online(self) -> dict[str, dict[str, Any]]:
        clients: dict[str, dict[str, Any]] = {}
        all_clients = await self.get_list()
        for client in all_clients.get("clients", []):
            if client.get("online") is True:
                clients[str(client["mac"])] = dict(client)
        return clients

    async def clear_cache(self) -> dict[str, Any]:
        response = await self._call("clients", "clear_cache")
        return dict(response)
