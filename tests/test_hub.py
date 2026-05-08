from __future__ import annotations

import types
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, MagicMock

from custom_components.ha_glinet.const import (
    CONF_ENABLED_FEATURES,
    FEATURE_REPEATER,
    FEATURE_WIREGUARD,
)
from custom_components.ha_glinet.hub import GLinetHub
from custom_components.ha_glinet.models import ClientDeviceInfo, RepeaterState, RepeaterStatus


def _hub_with_devices() -> GLinetHub:
    hub = GLinetHub.__new__(GLinetHub)
    hub._options = {"consider_home": 0}
    hub._factory_mac = "00:00:00:00:00:00"
    hub._host = "192.168.8.1"
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


async def test_fetch_all_data_skips_disabled_features(monkeypatch) -> None:
    hub = GLinetHub.__new__(GLinetHub)
    hub._settings = {CONF_ENABLED_FEATURES: [FEATURE_REPEATER]}
    hub._tailscale_config = {}
    hub._tailscale_connection = True
    hub._cellular_status = {"signal": 10}
    hub._modems = {"1-1": {}}
    hub._saved_networks = [{"ssid": "old"}]
    hub._entry = types.SimpleNamespace(entry_id="test_entry")
    hub._host = "192.168.8.1"
    hub.hass = object()

    called: list[str] = []

    async def fake_fetch_system_status() -> None:
        called.append("system")

    async def fake_fetch_connected_devices() -> None:
        called.append("clients")

    async def fake_fetch_wifi_interfaces() -> None:
        called.append("wifi")

    async def fake_fetch_wireguard_clients() -> None:
        called.append("wireguard")

    async def fake_fetch_repeater_status() -> None:
        called.append("repeater_status")

    async def fake_fetch_repeater_config() -> None:
        called.append("repeater_config")

    async def fake_fetch_saved_networks() -> None:
        called.append("saved_networks")

    async def fake_fetch_fan_status() -> None:
        called.append("fan")

    hub.fetch_system_status = fake_fetch_system_status
    hub.fetch_connected_devices = fake_fetch_connected_devices
    hub.fetch_wifi_interfaces = fake_fetch_wifi_interfaces
    hub.fetch_wireguard_clients = fake_fetch_wireguard_clients
    hub.fetch_repeater_status = fake_fetch_repeater_status
    hub.fetch_repeater_config = fake_fetch_repeater_config
    hub.fetch_saved_networks = fake_fetch_saved_networks
    hub.fetch_fan_status = fake_fetch_fan_status
    hub.refresh_session_token = _noop

    await hub.fetch_all_data()

    assert called == [
        "system",
        "clients",
        "wifi",
        "fan",
        "repeater_status",
        "repeater_config",
        "saved_networks",
    ]
    assert hub._tailscale_config == {}
    assert hub._tailscale_connection is None
    assert hub._cellular_status == {}
    assert hub._modems == {}


async def test_fetch_all_data_with_no_optional_features_still_runs_core_fetches(
    monkeypatch,
) -> None:
    hub = GLinetHub.__new__(GLinetHub)
    hub._settings = {CONF_ENABLED_FEATURES: []}
    hub._entry = types.SimpleNamespace(entry_id="test_entry")
    hub._host = "192.168.8.1"
    hub.hass = object()

    called: list[str] = []

    async def fake_fetch_system_status() -> None:
        called.append("system")

    async def fake_fetch_connected_devices() -> None:
        called.append("clients")

    async def fake_fetch_wifi_interfaces() -> None:
        called.append("wifi")

    async def fake_fetch_fan_status() -> None:
        called.append("fan")

    hub.fetch_system_status = fake_fetch_system_status
    hub.fetch_connected_devices = fake_fetch_connected_devices
    hub.fetch_wifi_interfaces = fake_fetch_wifi_interfaces
    hub.fetch_fan_status = fake_fetch_fan_status
    hub.refresh_session_token = _noop

    await hub.fetch_all_data()

    assert called == ["system", "clients", "wifi", "fan"]
    assert hub._wireguard_clients == {}
    assert hub._wireguard_connections is None
    assert hub._tailscale_config == {}
    assert hub._tailscale_connection is None
    assert hub._cellular_status == {}
    assert hub._modems == {}
    assert hub._repeater_status is None
    assert hub._repeater_config == {}
    assert hub._saved_networks == []


async def test_fetch_all_data_includes_wireguard_when_enabled(monkeypatch) -> None:
    hub = GLinetHub.__new__(GLinetHub)
    hub._settings = {CONF_ENABLED_FEATURES: [FEATURE_WIREGUARD]}
    hub._entry = types.SimpleNamespace(entry_id="test_entry")
    hub._host = "192.168.8.1"
    hub.hass = object()

    called: list[str] = []

    async def fake_fetch_system_status() -> None:
        called.append("system")

    async def fake_fetch_connected_devices() -> None:
        called.append("clients")

    async def fake_fetch_wifi_interfaces() -> None:
        called.append("wifi")

    async def fake_fetch_wireguard_clients() -> None:
        called.append("wireguard")

    async def fake_fetch_fan_status() -> None:
        called.append("fan")

    hub.fetch_system_status = fake_fetch_system_status
    hub.fetch_connected_devices = fake_fetch_connected_devices
    hub.fetch_wifi_interfaces = fake_fetch_wifi_interfaces
    hub.fetch_wireguard_clients = fake_fetch_wireguard_clients
    hub.fetch_fan_status = fake_fetch_fan_status
    hub.refresh_session_token = _noop

    await hub.fetch_all_data()

    assert called == ["system", "clients", "wifi", "fan", "wireguard"]


async def test_scan_wifi_networks_stores_results(monkeypatch) -> None:
    hub = GLinetHub.__new__(GLinetHub)
    hub._api = types.SimpleNamespace()
    hub._invoke_api = lambda api_callable: api_callable()
    hub._factory_mac = "00:00:00:00:00:00"
    hub.hass = object()
    hub._scanned_networks = []
    hub._last_wifi_scan = None

    async def fake_scan_wifi_networks(
        *, all_band: bool = False, dfs: bool = False
    ) -> list[dict[str, Any]]:
        return [
            {
                "ssid": "TestNet",
                "bssid": "aa:bb:cc:dd:ee:ff",
                "signal": -50,
                "band": "5g",
                "encryption": {"enabled": False, "description": "Open"},
                "saved": False,
                "channel": 36,
            }
        ]

    hub._api.scan_wifi_networks = fake_scan_wifi_networks

    calls: list[str] = []

    def fake_dispatcher_send(hass: Any, event: str) -> None:
        calls.append(event)

    import custom_components.ha_glinet.hub as hub_module

    monkeypatch.setattr(hub_module, "async_dispatcher_send", fake_dispatcher_send)

    networks = await hub.scan_wifi_networks(all_band=True, dfs=True)

    assert len(networks) == 1
    assert networks[0].ssid == "TestNet"
    assert hub._scanned_networks[0].ssid == "TestNet"
    assert hub._last_wifi_scan is not None
    assert calls == ["ha_glinet-networks-update-00:00:00:00:00:00"]


async def test_connect_to_wifi_calls_router_api_and_refreshes_status(monkeypatch) -> None:
    hub = GLinetHub.__new__(GLinetHub)
    called: list[Any] = []

    class RouterApi:
        async def connect_repeater(
            self,
            ssid: str,
            key: str | None = None,
            remember: bool = True,
            bssid: str | None = None,
        ) -> dict[str, Any]:
            called.append((ssid, key, remember, bssid))
            return {}

    async def fake_fetch_repeater_status() -> None:
        called.append("fetch_status")

    hub._api = RouterApi()
    hub._invoke_api = lambda api_callable: api_callable()
    hub.fetch_repeater_status = fake_fetch_repeater_status

    await hub.connect_to_wifi("test-ssid", "pass", remember=False, bssid="aa:bb")

    assert called == [("test-ssid", "pass", False, "aa:bb"), "fetch_status"]


async def test_disconnect_wifi_calls_router_api_and_refreshes_status(monkeypatch) -> None:
    hub = GLinetHub.__new__(GLinetHub)
    called: list[str] = []

    class RouterApi:
        async def disconnect_repeater(self) -> dict[str, Any]:
            called.append("disconnect")
            return {}

    async def fake_fetch_repeater_status() -> None:
        called.append("fetch_status")

    hub._api = RouterApi()
    hub._invoke_api = lambda api_callable: api_callable()
    hub.fetch_repeater_status = fake_fetch_repeater_status

    await hub.disconnect_wifi()

    assert called == ["disconnect", "fetch_status"]


async def test_set_repeater_band_updates_config(monkeypatch) -> None:
    hub = GLinetHub.__new__(GLinetHub)
    called: list[Any] = []

    class RouterApi:
        async def set_repeater_config(
            self, lock_band: str | None = None, **kwargs: Any
        ) -> dict[str, Any]:
            called.append(lock_band)
            return {}

    async def fake_fetch_repeater_config() -> None:
        called.append("fetch_config")

    hub._api = RouterApi()
    hub._invoke_api = lambda api_callable: api_callable()
    hub.fetch_repeater_config = fake_fetch_repeater_config

    await hub.set_repeater_band("5g")

    assert called == ["5g", "fetch_config"]


async def test_fetch_repeater_status_returns_none_when_unavailable() -> None:
    hub = GLinetHub.__new__(GLinetHub)
    hub._invoke_optional_api = AsyncMock(return_value=None)
    hub._api = SimpleNamespace(get_repeater_status=object())
    hub._repeater_status = RepeaterStatus(RepeaterState.CONNECTED)

    await hub.fetch_repeater_status()

    assert hub._repeater_status is None


async def test_fetch_repeater_config_stores_response() -> None:
    hub = GLinetHub.__new__(GLinetHub)
    hub._invoke_optional_api = AsyncMock(return_value={"lock_band": "2g"})
    hub._api = SimpleNamespace(get_repeater_config=object())

    await hub.fetch_repeater_config()

    assert hub._repeater_config == {"lock_band": "2g"}


async def test_get_saved_wifi_networks_and_remove_saved_wifi_network(monkeypatch) -> None:
    hub = GLinetHub.__new__(GLinetHub)
    api_calls: list[str] = []

    class RouterApi:
        async def get_saved_ap_list(self) -> list[dict[str, Any]]:
            api_calls.append("get_saved")
            return [{"ssid": "TestNet", "bssid": "aa:bb"}]

        async def remove_saved_ap(self, ssid: str) -> dict[str, Any]:
            api_calls.append(f"remove:{ssid}")
            return {}

    async def invoke_api(callable: Any) -> Any:
        return await callable()

    hub._api = RouterApi()
    hub._invoke_api = invoke_api

    saved = await hub.get_saved_wifi_networks()
    await hub.remove_saved_wifi_network("TestNet")

    assert saved == [{"ssid": "TestNet", "bssid": "aa:bb"}]
    assert api_calls == ["get_saved", "remove:TestNet", "get_saved"]


async def test_async_initialize_hub_cleans_up_orphaned_entities(monkeypatch) -> None:
    hub = GLinetHub.__new__(GLinetHub)
    hub._settings = {CONF_ENABLED_FEATURES: []} # All optional features disabled
    hub._entry = types.SimpleNamespace(entry_id="test_entry")
    hub.hass = MagicMock()
    hub._late_init_complete = True
    hub._factory_mac = "00:11:22:33:44:55"

    # Mock registry entries
    orphan_entry = types.SimpleNamespace(
        entity_id="sensor.glinet_cellular_signal",
        unique_id="glinet_sensor/00:11:22:33:44:55/cellular_signal",
        domain="sensor"
    )
    valid_entry = types.SimpleNamespace(
        entity_id="sensor.glinet_uptime",
        unique_id="glinet_sensor/00:11:22:33:44:55/system_uptime",
        domain="sensor"
    )

    mock_er = MagicMock()
    mock_er.async_remove = MagicMock()
    
    import homeassistant.helpers.entity_registry as er
    monkeypatch.setattr(er, "async_get", lambda _: mock_er)
    monkeypatch.setattr(
        er,
        "async_entries_for_config_entry",
        MagicMock(return_value=[orphan_entry, valid_entry]),
    )

    hub.refresh_session_token = _noop
    hub.fetch_all_data = _noop
    
    import custom_components.ha_glinet.hub as hub_module
    monkeypatch.setattr(hub_module, "async_track_time_interval", lambda *args: None)

    await hub.async_initialize_hub()

    # Verify cellular sensor (orphan) was removed but uptime (core) was not
    mock_er.async_remove.assert_called_once_with("sensor.glinet_cellular_signal")


async def _noop() -> None:
    return None
