from __future__ import annotations

import types
from typing import Any

from custom_components.ha_glinet.hub import GLinetHub
from custom_components.ha_glinet.models import ClientDeviceInfo


def _hub_with_devices() -> GLinetHub:
    hub = GLinetHub.__new__(GLinetHub)
    hub._options = {"consider_home": 0}
    hub._factory_mac = "00:00:00:00:00:00"
    hub._devices = {"aa:bb:cc:dd:ee:ff": ClientDeviceInfo("aa:bb:cc:dd:ee:ff")}
    hub._devices["aa:bb:cc:dd:ee:ff"].apply_update({"online": True})
    hub._invoke_api = _invoke_api_empty_clients
    hub._api = types.SimpleNamespace(get_online_clients=object())
    hub._entry = types.SimpleNamespace(entry_id="test_entry")
    hub.hass = object()
    return hub


async def _invoke_api_empty_clients(_: Any) -> dict[str, dict[str, Any]]:
    return {}


async def test_fetch_connected_devices_marks_existing_devices_away_on_empty_client_list(
    monkeypatch,
) -> None:
    calls: list[str] = []

    def fake_dispatcher_send(_: Any, event: str) -> None:
        calls.append(event)

    import custom_components.ha_glinet.hub as hub_module

    monkeypatch.setattr(hub_module, "async_dispatcher_send", fake_dispatcher_send)
    hub = _hub_with_devices()

    await hub.fetch_connected_devices()

    assert hub._devices["aa:bb:cc:dd:ee:ff"].is_connected is False
    assert calls == ["ha_glinet-device-update-00:00:00:00:00:00"]


async def test_fetch_tailscale_state_treats_timeout_as_optional() -> None:
    hub = GLinetHub.__new__(GLinetHub)
    hub._tailscale_config = {"enabled": True}
    hub._tailscale_connection = True

    async def invoke_optional_api(_: Any) -> None:
        return None

    hub._invoke_optional_api = invoke_optional_api
    hub._api = types.SimpleNamespace(get_tailscale_details=object())

    await hub.fetch_tailscale_state()

    assert hub._tailscale_config == {}
    assert hub._tailscale_connection is None


async def test_fetch_cellular_status_merges_modem_info_and_status() -> None:
    hub = GLinetHub.__new__(GLinetHub)
    hub._cached_modem_info = None
    hub._cellular_status = {}
    hub._default_modem_bus = None
    responses = [
        {"modems": [{"bus": "1-1", "sms_support": True, "name": "Quectel"}]},
        {"modems": [{"bus": "1-1", "simcard": {"carrier": "CMCC"}}]},
    ]

    async def invoke_optional_api(_: Any) -> dict[str, Any]:
        return responses.pop(0)

    hub._invoke_optional_api = invoke_optional_api
    hub._api = types.SimpleNamespace(get_modem_info=object(), get_cellular_status=object())

    await hub.fetch_cellular_status()

    assert hub.default_modem_bus == "1-1"
    assert hub.cellular_status["modems"] == [
        {
            "bus": "1-1",
            "sms_support": True,
            "name": "Quectel",
            "simcard": {"carrier": "CMCC"},
        }
    ]


async def test_send_sms_uses_default_modem_bus() -> None:
    hub = GLinetHub.__new__(GLinetHub)
    hub._default_modem_bus = "1-1"
    hub.fetch_sms_messages = _noop
    sent: list[tuple[str, str, str]] = []

    class RouterApi:
        async def send_sms(self, bus: str, recipient: str, text: str) -> dict[str, Any]:
            sent.append((bus, recipient, text))
            return {"response": "ok"}

    async def invoke_optional_api(api_callable: Any) -> dict[str, Any]:
        return await api_callable()

    hub._api = RouterApi()
    hub._invoke_optional_api = invoke_optional_api

    await hub.send_sms("+441234567890", "hello")

    assert sent == [("1-1", "+441234567890", "hello")]


async def _noop() -> None:
    return None
