from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .base import BaseModule

if TYPE_CHECKING:
    from ..client import GLinetApiClient


class BlackWhiteListModule(BaseModule):
    def __init__(self, client: GLinetApiClient) -> None:
        super().__init__(client)

    async def get_config(self) -> dict[str, Any]:
        return await self._call("black_white_list", "get_config")

    async def set_config(self, mode: str, mac: list[str]) -> dict[str, Any]:
        return await self._call(
            "black_white_list",
            "set_config",
            {"mode": mode, "mac": mac},
        )

    async def set_single_mac(self, mode: str, operate: str, mac: str) -> dict[str, Any]:
        return await self._call(
            "black_white_list",
            "set_single_mac",
            {"mode": mode, "operate": operate, "mac": mac},
        )
