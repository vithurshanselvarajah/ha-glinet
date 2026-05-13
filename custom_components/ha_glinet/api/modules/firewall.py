from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .base import BaseModule

if TYPE_CHECKING:
    from ..client import GLinetApiClient


class FirewallModule(BaseModule):
    def __init__(self, client: GLinetApiClient) -> None:
        super().__init__(client)

    async def get_rule_list(self) -> dict[str, Any]:
        return await self._call("firewall", "get_rule_list")

    async def add_rule(self, rule_params: dict[str, Any]) -> dict[str, Any]:
        return await self._call("firewall", "add_rule", rule_params)

    async def remove_rule(self, params: dict[str, Any]) -> dict[str, Any]:
        return await self._call("firewall", "remove_rule", params)

    async def get_dmz(self) -> dict[str, Any]:
        return await self._call("firewall", "get_dmz")

    async def set_dmz(self, enabled: bool, dest_ip: str | None = None) -> dict[str, Any]:
        params = {"enabled": enabled}
        if dest_ip:
            params["dest_ip"] = dest_ip
        return await self._call("firewall", "set_dmz", params)

    async def get_port_forward_list(self) -> dict[str, Any]:
        return await self._call("firewall", "get_port_forward_list")

    async def add_port_forward(self, forward_params: dict[str, Any]) -> dict[str, Any]:
        return await self._call("firewall", "add_port_forward", forward_params)

    async def remove_port_forward(self, params: dict[str, Any]) -> dict[str, Any]:
        return await self._call("firewall", "remove_port_forward", params)

    async def get_wan_access(self) -> dict[str, Any]:
        return await self._call("firewall", "get_wan_access")

    async def set_wan_access(self, config: dict[str, Any]) -> dict[str, Any]:
        return await self._call("firewall", "set_wan_access", config)

    async def get_zone_list(self) -> dict[str, Any]:
        return await self._call("firewall", "get_zone_list")
