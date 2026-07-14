from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .base import BaseModule

if TYPE_CHECKING:
    from ..client import GLinetApiClient


class ParentalControlModule(BaseModule):
    def __init__(self, client: GLinetApiClient) -> None:
        super().__init__(client)

    async def get_config(self) -> dict[str, Any]:
        return await self._call("parental-control", "get_config")

    async def set_config(self, enable: bool) -> dict[str, Any]:
        return await self._call(
            "parental-control",
            "set_config",
            {"enable": enable},
        )

    async def get_status(self) -> dict[str, Any]:
        return await self._call("parental-control", "get_status")

    async def get_brief(self, group_id: str) -> dict[str, Any]:
        return await self._call(
            "parental-control",
            "get_brief",
            {"group_id": group_id},
        )

    async def set_brief(
        self,
        enable: bool,
        time: str,
        rule_id: str,
        group_id: str,
        manual_stop: bool,
    ) -> dict[str, Any]:
        return await self._call(
            "parental-control",
            "set_brief",
            {
                "enable": enable,
                "time": time,
                "rule_id": rule_id,
                "group_id": group_id,
                "manual_stop": manual_stop,
            },
        )

    async def set_group(self, id: str, **kwargs: Any) -> dict[str, Any]:
        return await self._call("parental-control", "set_group", {"id": id, **kwargs})

    async def get_mode(self) -> dict[str, Any]:
        return await self._call("parental-control", "get_mode")

    async def set_mode(self, mode: int) -> dict[str, Any]:
        return await self._call("parental-control", "set_mode", {"mode": mode})

    async def update(self) -> dict[str, Any]:
        return await self._call("parental-control", "update")
