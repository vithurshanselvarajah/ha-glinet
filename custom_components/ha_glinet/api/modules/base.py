from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..client import GLinetApiClient


class BaseModule:
    """Base class for GL-INet API modules."""

    def __init__(self, client: GLinetApiClient) -> None:
        """Initialize the module."""
        self._client = client

    async def _call(
        self, module: str, method: str, params: dict[str, Any] | list[Any] | None = None
    ) -> dict[str, Any] | list[Any]:
        """Make a call to the router."""
        if params is None:
            params = {}
        payload = self._client._build_sid_payload("call", [module, method, params], self._client.sid)
        return await self._client._send_request(payload)
