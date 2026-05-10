from __future__ import annotations

from ..const import LONG_TIMEOUT
from .base import BaseModule


class DiagModule(BaseModule):
    async def ping(self, address: str) -> bool:
        payload = self._client._build_sid_payload(
            "call", ["diag", "ping", {"addr": address}], self._client.sid
        )
        response = await self._client._send_request(payload, timeout_seconds=LONG_TIMEOUT)
        return response != []
