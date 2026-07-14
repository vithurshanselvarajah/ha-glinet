from __future__ import annotations

from typing import Any

from .base import BaseModule


class McuModule(BaseModule):
    async def get_battery_config(self) -> dict[str, Any]:
        response = await self._call("mcu", "get_battery_config")
        return dict(response)

    async def set_battery_config(self, config: dict[str, Any]) -> dict[str, Any]:
        response = await self._call("mcu", "set_battery_config", config)
        return dict(response)

    async def get_oled_config(self) -> dict[str, Any]:
        response = await self._call("mcu", "get_config")
        return dict(response)

    async def set_oled_config(self, config: dict[str, Any]) -> dict[str, Any]:
        response = await self._call("mcu", "set_config", config)
        return dict(response)
