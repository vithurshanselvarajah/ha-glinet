from __future__ import annotations

from typing import Any

from ..const import LONG_TIMEOUT
from ..models import ModemInfo
from .base import BaseModule


class ModemModule(BaseModule):
    async def get_status(self) -> dict[str, Any]:
        response = await self._call("modem", "get_status")
        return dict(response)

    async def get_info(self) -> dict[str, Any]:
        response = await self._call("modem", "get_info")
        return dict(response)

    async def get_modem_info(self) -> list[ModemInfo]:
        info_response = await self.get_info()
        status_response = await self.get_status()
        
        info_modems = info_response.get("modems", [])
        status_modems = status_response.get("modems", [])
        
        merged: dict[str, dict[str, Any]] = {}
        for modem in [*info_modems, *status_modems]:
            if not isinstance(modem, dict) or not modem.get("bus"):
                continue
            bus = str(modem["bus"])
            merged[bus] = merged.get(bus, {}) | dict(modem)
            
        return [
            ModemInfo(
                bus=str(modem.get("bus", "")),
                model=str(modem.get("model", "")),
                imei=str(modem.get("imei", "")),
                iccid=str(modem.get("iccid") or modem.get("simcard", {}).get("iccid", "")),
                status=str(modem.get("status", "")),
                signal=modem.get("signal"),
                network_type=str(
                    modem.get("network_type")
                    or modem.get("simcard", {}).get("network_type")
                    or modem.get("simcard", {}).get("signal", {}).get("network_type", "")
                ),
                apn=str(modem.get("apn") or modem.get("simcard", {}).get("apn", "")),
            )
            for modem in merged.values()
        ]

    async def get_sms_list(self) -> list[dict[str, Any]]:
        response = await self._call("modem", "get_sms_list")
        if isinstance(response, list):
            return [dict(item) for item in response]
        messages = dict(response).get("list", [])
        return [dict(item) for item in messages]

    async def send_sms(
        self,
        bus: str,
        recipient: str,
        text: str,
        timeout: int = 10,
    ) -> dict[str, Any]:
        payload = self._client._build_sid_payload(
            "call",
            [
                "modem",
                "send_sms",
                {
                    "bus": bus,
                    "phone_number": recipient,
                    "body": text,
                    "timeout": timeout,
                },
            ],
            self._client.sid,
        )
        response = await self._client._send_request(
            payload,
            timeout_seconds=max(LONG_TIMEOUT, timeout + 2),
        )
        return dict(response)

    async def remove_sms(
        self, bus: str, scope: int, message_id: str | None = None
    ) -> dict[str, Any]:
        params = {"bus": bus, "scope": scope}
        if message_id:
            params["name"] = message_id
        response = await self._call("modem", "remove_sms", params)
        return dict(response)
