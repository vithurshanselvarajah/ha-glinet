from typing import Any

import pytest

from custom_components.ha_glinet.api.client import (
    GLinetApiClient,
    _decode_firmware_version,
    _extract_response_data,
)
from custom_components.ha_glinet.api.exceptions import (
    APIClientError,
    AuthenticationError,
    NonZeroResponse,
    TokenError,
    UnsuccessfulRequest,
)
from custom_components.ha_glinet.api.models import WifiInterfaceInfo


class FakeResponse:
    def __init__(
        self,
        payload: dict[str, Any] | list[Any] | Exception,
        status: int = 200,
        text: str = "not-json",
    ) -> None:
        self._payload = payload
        self.status = status
        self._text = text

    async def json(self, content_type: str | None = None) -> dict[str, Any] | list[Any]:
        assert content_type is None
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload

    async def text(self) -> str:
        return self._text


class FakePostContext:
    def __init__(self, response: FakeResponse) -> None:
        self._response = response

    async def __aenter__(self) -> FakeResponse:
        return self._response

    async def __aexit__(self, *_: Any) -> None:
        return None


class FakeSession:
    def __init__(self, responses: list[Any]) -> None:
        self.responses = list(responses)
        self.requests: list[dict[str, Any]] = []

    def post(self, url: str, json: dict[str, Any], timeout: int) -> FakePostContext:
        self.requests.append({"url": url, "json": json, "timeout": timeout})
        payload = self.responses.pop(0)
        if isinstance(payload, FakeResponse):
            return FakePostContext(payload)
        return FakePostContext(FakeResponse(payload))

@pytest.mark.parametrize(
    ("version", "expected"),
    [
        ("4.8.0", (4, 8, 0, 0)),
        ("v4.7.2-release6", (4, 7, 2, 6)),
        ("3", (3, 0, 0, 0)),
        ("snapshot", (0, 0, 0, 0)),
    ],
)
def test_decode_firmware_version_normalizes_to_four_numbers(
    version: str,
    expected: tuple[int, int, int, int],
) -> None:
    assert _decode_firmware_version(version) == expected


async def test_extract_response_data_returns_result() -> None:
    response = FakeResponse({"jsonrpc": "2.0", "result": {"ok": True}, "id": 0})

    assert await _extract_response_data(response) == {"ok": True}


@pytest.mark.parametrize(
    ("code", "exception"),
    [
        (-1, TokenError),
        (-32000, AuthenticationError),
        (-32001, NonZeroResponse),
    ],
)
async def test_extract_response_data_maps_router_errors(
    code: int,
    exception: type[Exception],
) -> None:
    response = FakeResponse({"jsonrpc": "2.0", "error": {"code": code, "message": "nope"}})

    with pytest.raises(exception):
        await _extract_response_data(response)


async def test_extract_response_data_rejects_http_errors() -> None:
    response = FakeResponse({"error": {"code": 500}}, status=500)

    with pytest.raises(UnsuccessfulRequest):
        await _extract_response_data(response)


async def test_extract_response_data_rejects_invalid_json() -> None:
    response = FakeResponse(ValueError("bad json"), text="<html>bad</html>")

    with pytest.raises(UnsuccessfulRequest):
        await _extract_response_data(response)


async def test_extract_response_data_rejects_unexpected_payload_shape() -> None:
    response = FakeResponse({"jsonrpc": "2.0", "id": 0})

    with pytest.raises(APIClientError):
        await _extract_response_data(response)


async def test_get_online_clients_filters_offline_clients() -> None:
    session = FakeSession(
        [
            {
                "result": {
                    "clients": [
                        {"mac": "aa:aa:aa:aa:aa:aa", "online": True, "name": "phone"},
                        {"mac": "bb:bb:bb:bb:bb:bb", "online": False, "name": "laptop"},
                    ]
                }
            }
        ]
    )
    client = GLinetApiClient("http://router/rpc", session, sid="sid-1")

    assert await client.clients.get_online() == {
        "aa:aa:aa:aa:aa:aa": {"mac": "aa:aa:aa:aa:aa:aa", "online": True, "name": "phone"}
    }


async def test_get_wifi_interfaces_returns_models() -> None:
    session = FakeSession(
        [
            {
                "result": {
                    "res": [
                        {
                            "ifaces": [
                                {
                                    "name": "wlan0",
                                    "ssid": "Main",
                                    "key": "secret",
                                    "enabled": True,
                                    "encryption": "psk2",
                                },
                                {"ssid": "Missing name", "key": "secret"},
                            ]
                        }
                    ]
                }
            }
        ]
    )
    client = GLinetApiClient("http://router/rpc", session, sid="sid-1")

    assert await client.wifi.get_interfaces() == {
        "wlan0": WifiInterfaceInfo(
            enabled=True, ssid="Main", guest=False, hidden=False, encryption="psk2"
        )
    }


async def test_sms_methods_use_sms_module_payloads() -> None:
    session = FakeSession(
        [
            {"result": {"list": [{"name": "sms-1", "body": "hello"}]}},
            {"result": {"sent": True}},
        ]
    )
    client = GLinetApiClient("http://router/rpc", session, sid="sid-1")

    assert await client.modem.get_sms_list() == [{"name": "sms-1", "body": "hello"}]
    assert await client.modem.send_sms("1-1", "+441234567890", "hi") == {"sent": True}

    assert session.requests[0]["json"]["params"] == ["sid-1", "modem", "get_sms_list", {}]
    assert session.requests[1]["json"]["params"] == [
        "sid-1",
        "modem",
        "send_sms",
        {
            "bus": "1-1",
            "phone_number": "+441234567890",
            "body": "hi",
            "timeout": 10,
        },
    ]


async def test_get_modem_info_uses_documented_modem_endpoint() -> None:
    session = FakeSession([{"result": {"modems": [{"bus": "1-1"}]}}])
    client = GLinetApiClient("http://router/rpc", session, sid="sid-1")

    assert await client.modem.get_info() == {"modems": [{"bus": "1-1"}]}
    assert session.requests[0]["json"]["params"] == ["sid-1", "modem", "get_info", {}]


async def test_wireguard_state_uses_new_vpn_client_module_for_new_firmware() -> None:
    session = FakeSession([{"result": {"status_list": [{"type": "wireguard", "peer_id": 7}]}}])
    client = GLinetApiClient("http://router/rpc", session, sid="sid-1")
    client._firmware_version = (4, 8, 0, 0)

    assert await client.vpn.get_wireguard_state() == [{"type": "wireguard", "peer_id": 7}]
    assert session.requests[0]["json"]["params"] == ["sid-1", "vpn-client", "get_status", {}]


async def test_wireguard_state_uses_legacy_module_for_old_firmware() -> None:
    session = FakeSession([{"result": {"status": 1, "peer_id": 7}}])
    client = GLinetApiClient("http://router/rpc", session, sid="sid-1")
    client._firmware_version = (4, 7, 9, 0)

    assert await client.vpn.get_wireguard_state() == [{"status": 1, "peer_id": 7}]
    assert session.requests[0]["json"]["params"] == ["sid-1", "wg-client", "get_status", {}]
