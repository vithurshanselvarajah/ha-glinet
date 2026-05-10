from __future__ import annotations

from typing import Any

from .base import BaseModule


class LedModule(BaseModule):
    async def get_config(self) -> dict[str, Any]:
        response = await self._call("led", "get_config")
        return dict(response)

    async def set_config(self, config: dict[str, Any]) -> dict[str, Any]:
        response = await self._call("led", "set_config", config)
        return dict(response)
