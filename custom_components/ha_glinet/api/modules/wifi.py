from __future__ import annotations

from typing import Any
from .base import BaseModule

class WifiModule(BaseModule):
    async def get_config(self) -> dict[str, Any]:
        response = await self._call("wifi", "get_config")
        return dict(response)

    async def set_config(self, config: dict[str, Any]) -> dict[str, Any]:
        response = await self._call("wifi", "set_config", config)
        return dict(response)

    async def get_interfaces(self, redact_keys: bool = True) -> dict[str, dict[str, Any]]:
        wifi_config = await self.get_config()
        result: dict[str, dict[str, Any]] = {}
        for device in wifi_config.get("res", []):
            for iface in device.get("ifaces", []):
                iface_name = iface.get("name")
                if not iface_name:
                    continue
                result[iface_name] = {
                    **iface,
                    "key": None if redact_keys else iface.get("key"),
                }
        return result

    async def set_interface_enabled(self, iface_name: str, enabled: bool) -> dict[str, Any]:
        ifaces = await self.get_interfaces()
        if iface_name not in ifaces:
            raise ValueError("iface_name does not exist")
        return await self.set_config({"enabled": enabled, "iface_name": iface_name})
