from __future__ import annotations

from typing import Any

from .base import BaseModule


class KmwanModule(BaseModule):
    async def get_config(self) -> dict[str, Any]:
        response = await self._call("kmwan", "get_config")
        return dict(response)

    async def get_status(self) -> dict[str, Any]:
        response = await self._call("kmwan", "get_status")
        return dict(response)

    async def set_config(self, config: dict[str, Any]) -> dict[str, Any]:
        response = await self._call("kmwan", "set_config", config)
        return dict(response) if response else {}

    async def set_interface(self, interface: dict[str, Any]) -> dict[str, Any]:
        response = await self._call("kmwan", "set_interface", interface)
        return dict(response) if response else {}

    async def set_sensitivity(self, sensitivity: dict[str, Any]) -> dict[str, Any]:
        response = await self._call("kmwan", "set_sensitivity", sensitivity)
        return dict(response) if response else {}
