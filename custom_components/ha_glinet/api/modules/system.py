from __future__ import annotations

from typing import Any

from ..models import RouterStatus, SystemInfo
from ..utils import decode_firmware_version
from .base import BaseModule


class SystemModule(BaseModule):
    async def get_info(self) -> SystemInfo:
        response = await self._call("system", "get_info")
        info = dict(response)
        firmware_version = info.get("firmware_version", "")
        if firmware_version:
            self._client._firmware_version = decode_firmware_version(str(firmware_version))
        return SystemInfo(
            model=info.get("model", ""),
            firmware_version=str(firmware_version),
            mac=info.get("mac", ""),
            sn=info.get("sn", ""),
            device_id=info.get("device_id", ""),
        )

    async def get_status(self) -> RouterStatus:
        response = await self._call("system", "get_status")
        status = dict(response)
        sys_info = status.get("system", {})
        
        def _get(key, default=None):
            val = status.get(key)
            if val is None:
                val = sys_info.get(key)
            return val if val is not None else default

        load_average = (
            _get("load_average") 
            or _get("loadavg") 
            or []
        )
        
        cpu = status.get("cpu") or sys_info.get("cpu") or {}
        temperature = cpu.get("temperature")
        if temperature is None:
            temperature = cpu.get("temp")
        if temperature is None:
            temperature = _get("temperature")
        if temperature is None:
            temperature = _get("temp")

        return RouterStatus(
            uptime=_get("uptime", 0),
            load_average=load_average,
            memory_total=_get("memory_total", 0),
            memory_free=_get("memory_free", 0),
            memory_shared=_get("memory_shared", 0),
            memory_buffered=_get("memory_buffered") or _get("memory_buff_cache") or 0,
            temperature=temperature,
            flash_total=_get("flash_total", 0),
            flash_free=_get("flash_free", 0),
        )

    async def get_load(self) -> dict[str, Any]:
        response = await self._call("system", "get_load")
        return dict(response)

    async def reboot(self, delay: int = 0) -> dict[str, Any]:
        response = await self._call("system", "reboot", {"delay": delay})
        return dict(response)
