from typing import Any

from .base import BaseModule


class ZeroTierModule(BaseModule):
    async def get_config(self) -> dict[str, Any]:
        response = await self._call("zerotier", "get_config")
        return dict(response)

    async def get_status(self) -> dict[str, Any]:
        response = await self._call("zerotier", "get_status")
        return dict(response)

    async def set_config(self, params: dict[str, Any]) -> dict[str, Any]:
        response = await self._call("zerotier", "set_config", params)
        return dict(response)
