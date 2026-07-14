from __future__ import annotations

from typing import Any

from .base import BaseModule


class FanModule(BaseModule):
    async def get_status(self) -> dict[str, Any]:
        response = await self._call("fan", "get_status")
        return dict(response)

    async def get_config(self) -> dict[str, Any]:
        response = await self._call("fan", "get_config")
        return dict(response)

    async def set_config(self, temperature: int) -> dict[str, Any]:
        response = await self._call("fan", "set_config", {"temperature": temperature})
        return dict(response) if response else {}

    async def set_test(self, test: bool = True, time: int = 10) -> dict[str, Any]:
        response = await self._call("fan", "set_test", {"test": test, "time": time})
        return dict(response) if response else {}
