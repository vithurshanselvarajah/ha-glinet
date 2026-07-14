from __future__ import annotations

from typing import Any

from ..const import FIRMWARE_4_9, LONG_TIMEOUT
from ..exceptions import NonZeroResponse
from ..models import ModemInfo
from .base import BaseModule


class ModemModule(BaseModule):
    async def get_status(self) -> dict[str, Any]:
        if await self._uses_modem_49_api:
            return await self._get_status_49()
        response = await self._call("modem", "get_status")
        return dict(response)

    async def get_info(self) -> dict[str, Any]:
        if await self._uses_modem_49_api:
            return await self._get_info_49()
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
        if await self._uses_modem_49_api:
            return await self._get_sms_list_49()
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
        slot: int | str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {
            "bus": bus,
            "phone_number": recipient,
            "body": text,
            "timeout": timeout,
        }
        if slot is not None:
            params["slot"] = slot
        payload = self._client._build_sid_payload(
            "call",
            ["modem", "send_sms", params],
            self._client.sid,
        )
        response = await self._client._send_request(
            payload,
            timeout_seconds=max(LONG_TIMEOUT, timeout + 2),
        )
        return dict(response)

    async def remove_sms(
        self,
        bus: str,
        scope: int,
        message_id: str | None = None,
        slot: int | str | None = None,
    ) -> dict[str, Any]:
        params = {"bus": bus, "scope": scope}
        if message_id:
            params["name"] = message_id
        if slot is not None:
            params["slot"] = slot
        response = await self._call("modem", "remove_sms", params)
        return dict(response)

    @property
    async def _uses_modem_49_api(self) -> bool:
        return await self._client._is_firmware_at_least(FIRMWARE_4_9)

    async def _get_info_49(self) -> dict[str, Any]:
        status = await self._get_status_49()
        modems = [
            {
                "bus": modem["bus"],
                "slot": modem.get("slot"),
                "iccid": modem.get("iccid", ""),
                "sms_support": True,
            }
            for modem in status.get("modems", [])
            if isinstance(modem, dict) and modem.get("bus")
        ]
        return {"modems": modems}

    async def _get_status_49(self) -> dict[str, Any]:
        targets = await self._get_modem_49_targets()
        try:
            signals_response = await self._call("modem", "get_signals", {"time": 10})
            signals = _latest_signals_by_slot(dict(signals_response).get("signals", []))
        except NonZeroResponse:
            signals = {}

        modems: list[dict[str, Any]] = []
        for target in targets:
            modem = await self._get_modem_49_status(target, signals)
            if modem is not None:
                modems.append(modem)
        return {"modems": modems}

    async def _get_modem_49_targets(self) -> list[dict[str, Any]]:
        response = await self._call("modem", "get_modem_current_interface")
        interfaces = dict(response).get("interfaces", [])
        targets = [
            target
            for interface in interfaces
            if isinstance(interface, str)
            for target in _targets_from_interface(interface)
        ]
        if targets:
            return _deduplicate_targets(targets)
        return [{"bus": "cpu", "slot": 1}, {"bus": "cpu", "slot": 2}]

    async def _get_modem_49_status(
        self,
        target: dict[str, Any],
        signals: dict[str, dict[str, Any]],
    ) -> dict[str, Any] | None:
        params = dict(target)
        try:
            network_status_response = await self._call(
                "modem", "get_network_status", params
            )
            network_info_response = await self._call("modem", "get_network_info", params)
        except NonZeroResponse:
            return None

        network_status = _first_dict(dict(network_status_response).get("networks"))
        network_info = _first_dict(dict(network_info_response).get("networks"))
        signal = signals.get(str(target.get("slot", "")), {})
        cell_info = dict(network_info.get("cell_info") or {})
        bus = str(network_status.get("bus") or network_info.get("bus") or target["bus"])
        slot = network_status.get("slot") or network_info.get("slot") or target.get("slot")
        network_type = signal.get("network_type") or cell_info.get("mode") or ""

        return {
            "bus": bus,
            "slot": slot,
            "iccid": network_status.get("iccid", ""),
            "status": network_status.get("status"),
            "dial_status": network_status.get("dial_status"),
            "signal": signal.get("strength"),
            "network_type": network_type,
            "simcard": {
                "iccid": network_status.get("iccid", ""),
                "network_type": network_type,
                "signal": signal,
            },
            "network": {
                "ipv4": _normalize_ip_info(network_info.get("ipv4")),
                "ipv6": _normalize_ip_info(network_info.get("ipv6")),
            },
            "cell_info": cell_info,
            "traffic_total": network_status.get("traffic_total"),
            "protocol": network_status.get("protocol"),
            "network_interface": network_info.get("network_interface"),
        }

    async def _get_sms_list_49(self) -> list[dict[str, Any]]:
        targets = await self._get_modem_49_targets()
        messages: list[dict[str, Any]] = []
        for bus in dict.fromkeys(str(target["bus"]) for target in targets):
            try:
                response = await self._call("modem", "get_sms_list", {"bus": bus})
            except NonZeroResponse:
                continue
            if isinstance(response, list):
                messages.extend(dict(item) for item in response)
            else:
                messages.extend(dict(item) for item in dict(response).get("list", []))
        return messages


def _targets_from_interface(interface: str) -> list[dict[str, Any]]:
    if not interface.startswith("modem_"):
        return []

    value = interface.removeprefix("modem_")
    slot: int | None = None
    if "_s" in value:
        bus_part, _, slot_part = value.rpartition("_s")
        if slot_part.isdigit():
            value = bus_part
            slot = int(slot_part)

    if value == "cpu":
        if slot is None:
            return [{"bus": "cpu", "slot": 1}, {"bus": "cpu", "slot": 2}]
        return [{"bus": "cpu", "slot": slot}]

    parts = [part for part in value.split("_") if part]
    if len(parts) < 2:
        return []
    bus = "-".join(parts[:2])
    if len(parts) > 2:
        bus = f"{bus}.{'.'.join(parts[2:])}"

    target: dict[str, Any] = {"bus": bus}
    if slot is not None:
        target["slot"] = slot
    return [target]


def _deduplicate_targets(targets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduplicated: dict[tuple[str, str], dict[str, Any]] = {}
    for target in targets:
        key = (str(target.get("bus", "")), str(target.get("slot", "")))
        deduplicated[key] = target
    return list(deduplicated.values())


def _latest_signals_by_slot(signals: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(signals, list):
        return {}
    latest: dict[str, dict[str, Any]] = {}
    for signal in signals:
        if not isinstance(signal, dict) or signal.get("slot") in (None, ""):
            continue
        key = str(signal["slot"])
        current = latest.get(key)
        if current is None or _signal_timestamp(signal) >= _signal_timestamp(current):
            latest[key] = dict(signal)
    return latest


def _signal_timestamp(signal: dict[str, Any]) -> int:
    try:
        return int(signal.get("timestamp", 0))
    except (TypeError, ValueError):
        return 0


def _first_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                return dict(item)
    if isinstance(value, dict):
        return dict(value)
    return {}


def _normalize_ip_info(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return dict(value)
    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                return dict(item)
            if item not in (None, ""):
                return {"ip": str(item)}
        return {}
    if value not in (None, ""):
        return {"ip": str(value)}
    return {}
