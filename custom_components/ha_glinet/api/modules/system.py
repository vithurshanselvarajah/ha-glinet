from __future__ import annotations

from typing import Any
from .base import BaseModule
from ..utils import decode_firmware_version

class SystemModule(BaseModule):
    async def get_info(self) -> dict[str, Any]:
        response = await self._call("system", "get_info")
        info = dict(response)
        firmware_version = info.get("firmware_version")
        if firmware_version:
            self._client._firmware_version = decode_firmware_version(str(firmware_version))
        return info

    async def get_status(self) -> dict[str, Any]:
        response = await self._call("system", "get_status")
        status = dict(response)
        if "wifi" in status:
            for wifi in status["wifi"]:
                wifi["passwd"] = None
        return status

    async def get_load(self) -> dict[str, Any]:
        response = await self._call("system", "get_load")
        return dict(response)

    async def reboot(self, delay: int = 0) -> dict[str, Any]:
        response = await self._call("system", "reboot", {"delay": delay})
        return dict(response)
