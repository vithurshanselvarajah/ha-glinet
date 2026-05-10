from __future__ import annotations

from typing import Any

from ..const import LONG_TIMEOUT, SCAN_TIMEOUT
from .base import BaseModule


class RepeaterModule(BaseModule):
    async def get_status(self) -> dict[str, Any]:
        response = await self._call("repeater", "get_status")
        return dict(response)

    async def get_config(self) -> dict[str, Any]:
        response = await self._call("repeater", "get_config")
        return dict(response)

    async def set_config(self, params: dict[str, Any]) -> dict[str, Any]:
        response = await self._call("repeater", "set_config", params)
        return dict(response) if response else {}

    async def scan(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        payload = self._client._build_sid_payload(
            "call", ["repeater", "scan", params], self._client.sid
        )
        response = await self._client._send_request(payload, timeout_seconds=SCAN_TIMEOUT)
        return list(dict(response).get("res", []))

    async def connect(self, params: dict[str, Any]) -> dict[str, Any]:
        payload = self._client._build_sid_payload(
            "call", ["repeater", "connect", params], self._client.sid
        )
        response = await self._client._send_request(payload, timeout_seconds=LONG_TIMEOUT)
        return dict(response) if response else {}

    async def disconnect(self) -> dict[str, Any]:
        response = await self._call("repeater", "disconnect")
        return dict(response) if response else {}

    async def get_saved_ap_list(self) -> list[dict[str, Any]]:
        response = await self._call("repeater", "get_saved_ap_list")
        return list(dict(response).get("res", []))

    async def remove_saved_ap(self, ssid: str) -> dict[str, Any]:
        response = await self._call("repeater", "remove_saved_ap", {"ssid": ssid})
        return dict(response) if response else {}
