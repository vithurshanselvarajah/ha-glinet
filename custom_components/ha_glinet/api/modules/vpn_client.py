from __future__ import annotations

from typing import Any

from .base import BaseModule


class VpnClientModule(BaseModule):
    async def get_status(self) -> dict[str, Any]:
        response = await self._call("vpn-client", "get_status")
        return dict(response)

    async def get_tunnel(self) -> dict[str, Any]:
        response = await self._call("vpn-client", "get_tunnel")
        return dict(response)

    async def set_tunnel(
        self, tunnel_id: int, enabled: bool, via: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        params = {"enabled": enabled, "tunnel_id": tunnel_id}
        if via:
            params["via"] = via
        response = await self._call("vpn-client", "set_tunnel", params)
        return dict(response)
