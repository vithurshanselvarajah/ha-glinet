from __future__ import annotations

from typing import Any

from .base import BaseModule


class UpgradeModule(BaseModule):
    async def check_firmware_online(self) -> dict[str, Any]:
        response = await self._call("upgrade", "check_firmware_online")
        return dict(response)

    async def get_config(self) -> dict[str, Any]:
        response = await self._call("upgrade", "get_config")
        return dict(response)

    async def get_online_upgrade_status(self) -> dict[str, Any]:
        response = await self._call("upgrade", "get_online_upgrade_status")
        return dict(response)

    async def upgrade_online(self, params: dict[str, Any]) -> dict[str, Any]:
        response = await self._call("upgrade", "upgrade_online", params)
        return dict(response) if response else {}
