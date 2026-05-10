from __future__ import annotations

from typing import Any
from .base import BaseModule

class MacCloneModule(BaseModule):
    async def get_mac(self) -> dict[str, Any]:
        response = await self._call("macclone", "get_mac")
        return dict(response)
