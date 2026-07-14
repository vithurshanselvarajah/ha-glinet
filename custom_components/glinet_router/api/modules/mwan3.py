from __future__ import annotations

from typing import Any

from .base import BaseModule


class Mwan3Module(BaseModule):
    async def get_config(self) -> dict[str, Any]:
        response = await self._call("mwan3", "get_config")
        return dict(response)

    async def get_status(self) -> dict[str, Any]:
        response = await self._call("mwan3", "get_status")
        return dict(response)

    async def set_config(self, config: dict[str, Any]) -> dict[str, Any]:
        response = await self._call("mwan3", "set_config", config)
        return dict(response) if response else {}

    async def set_interface(self, interface: dict[str, Any]) -> dict[str, Any]:
        response = await self._call("mwan3", "set_interface", interface)
        return dict(response) if response else {}
