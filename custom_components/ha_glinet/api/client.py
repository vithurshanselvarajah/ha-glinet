from __future__ import annotations

import asyncio
import hashlib
import re
from typing import Any

from aiohttp import ClientResponse, ClientSession
from passlib.hash import md5_crypt, sha256_crypt, sha512_crypt

from .exceptions import (
    APIClientError,
    AuthenticationError,
    NonZeroResponse,
    TokenError,
    UnsuccessfulRequest,
)
from .models import TailscaleConnection

DEFAULT_TIMEOUT = 2
LONG_TIMEOUT = 5
SCAN_TIMEOUT = 30
NEW_VPN_CLIENT_VERSION = (4, 8, 0, 0)


def _decode_firmware_version(version: str) -> tuple[int, int, int, int]:
    numbers = [int(value) for value in re.findall(r"\d+", version)]
    normalized = [*numbers, 0, 0, 0, 0][:4]
    return tuple(normalized)


async def _extract_response_data(response: ClientResponse) -> dict[str, Any] | list[Any]:
    try:
        payload = await response.json(content_type=None)
    except Exception as exc:
        text = await response.text()
        raise UnsuccessfulRequest(
            f"Request failed or returned invalid JSON (status {response.status}): {text}"
        ) from exc

    if not 200 <= response.status < 300:
        raise UnsuccessfulRequest(f"Request failed with status {response.status}: {payload}")

    if "result" in payload:
        return payload["result"]

    if "error" not in payload:
        raise APIClientError(f"Unexpected response from GL-INet router: {payload}")

    error = payload["error"]
    message = error.get("message", "null")
    code = error.get("code", 0)

    if code == -1:
        raise TokenError(f"Request returned error code -1 ({message})")
    if code == -32000:
        raise AuthenticationError(f"Request returned error code -32000 ({message})")
    if code < 0:
        raise NonZeroResponse(f"Request returned error code {code} with message: {message}")

    return payload


class GLinetApiClient:
    _firmware_version: tuple[int, int, int, int] | None = None

    def __init__(
        self,
        base_url: str,
        session: ClientSession,
        sid: str | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._session = session
        self.sid = sid
        self._logged_in = sid is not None

    @staticmethod
    def _build_sid_payload(method: str, params: list[Any], sid: str | None) -> dict[str, Any]:
        return {
            "method": method,
            "jsonrpc": "2.0",
            "params": [sid, *params],
            "id": 0,
        }

    @staticmethod
    def _build_payload(method: str, params: dict[str, Any]) -> dict[str, Any]:
        return {
            "method": method,
            "jsonrpc": "2.0",
            "params": params,
            "id": 0,
        }

    async def _send_request(
        self, payload: dict[str, Any], timeout_seconds: int = DEFAULT_TIMEOUT
    ) -> dict[str, Any] | list[Any]:
        async with self._session.post(
            self._base_url,
            json=payload,
            timeout=timeout_seconds,
        ) as response:
            return await _extract_response_data(response)

    async def _request_challenge(self, username: str) -> dict[str, Any]:
        result = await self._send_request(self._build_payload("challenge", {"username": username}))
        return dict(result)

    async def _fetch_session_id(self, username: str, login_hash: str) -> dict[str, Any]:
        result = await self._send_request(
            self._build_payload("login", {"username": username, "hash": login_hash})
        )
        return dict(result)

    async def is_router_reachable(self, username: str = "root") -> bool:
        try:
            return bool(await self._request_challenge(username))
        except APIClientError:
            return False

    async def authenticate(self, username: str, password: str) -> None:
        def _compute_hash(
            algorithm: int,
            salt: str,
            nonce: str,
            hash_method: str,
            login_username: str,
            login_password: str,
        ) -> str:
            if algorithm == 1:
                cipher_password = md5_crypt.using(salt=salt).hash(login_password)
            elif algorithm == 5:
                cipher_password = sha256_crypt.using(salt=salt, rounds=5000).hash(
                    login_password
                )
            elif algorithm == 6:
                cipher_password = sha512_crypt.using(salt=salt, rounds=5000).hash(
                    login_password
                )
            else:
                raise ValueError("Unsupported router cipher algorithm")

            data = f"{login_username}:{cipher_password}:{nonce}"
            if hash_method == "md5":
                return hashlib.md5(data.encode(), usedforsecurity=False).hexdigest()
            if hash_method == "sha256":
                return hashlib.sha256(data.encode()).hexdigest()
            if hash_method == "sha512":
                return hashlib.sha512(data.encode()).hexdigest()
            raise ValueError("Unsupported router hash algorithm")

        challenge = await self._request_challenge(username)
        login_hash = await asyncio.to_thread(
            _compute_hash,
            challenge["alg"],
            challenge["salt"],
            challenge["nonce"],
            challenge.get("hash-method", "md5"),
            username,
            password,
        )
        response = await self._fetch_session_id(username, login_hash)
        if "sid" not in response:
            raise AuthenticationError("Router login response did not include a session id")
        self.sid = str(response["sid"])
        self._logged_in = True

    async def get_router_info(self) -> dict[str, Any]:
        response = await self._send_request(
            self._build_sid_payload("call", ["system", "get_info"], self.sid)
        )
        info = dict(response)
        firmware_version = info.get("firmware_version")
        if not firmware_version:
            raise ValueError("No firmware version found in router info")
        self._firmware_version = _decode_firmware_version(str(firmware_version))
        return info

    async def get_router_status(self) -> dict[str, Any]:
        response = await self._send_request(
            self._build_sid_payload("call", ["system", "get_status"], self.sid)
        )
        status = dict(response)
        if "wifi" in status:
            for wifi in status["wifi"]:
                wifi["passwd"] = None
        return status

    async def get_router_load(self) -> dict[str, Any]:
        response = await self._send_request(
            self._build_sid_payload("call", ["system", "get_load"], self.sid)
        )
        return dict(response)

    async def get_router_mac(self) -> dict[str, Any]:
        response = await self._send_request(
            self._build_sid_payload("call", ["macclone", "get_mac"], self.sid)
        )
        return dict(response)

    async def reboot_router(self, delay: int = 0) -> dict[str, Any]:
        response = await self._send_request(
            self._build_sid_payload("call", ["system", "reboot", {"delay": delay}], self.sid)
        )
        return dict(response)

    async def ping_address(self, address: str) -> bool:
        response = await self._send_request(
            self._build_sid_payload("call", ["diag", "ping", {"addr": address}], self.sid),
            timeout_seconds=LONG_TIMEOUT,
        )
        return response != []

    async def get_internet_status(self) -> dict[str, Any]:
        response = await self._send_request(
            self._build_sid_payload("call", ["edgerouter", "get_status"], self.sid)
        )
        return dict(response)

    async def get_led_status(self) -> dict[str, Any]:
        response = await self._send_request(
            self._build_sid_payload("call", ["led", "get_config"], self.sid)
        )
        return dict(response)

    async def set_led_enabled(self, enabled: bool) -> dict[str, Any]:
        response = await self._send_request(
            self._build_sid_payload("call", ["led", "set_config", {"enable": enabled}], self.sid)
        )
        return dict(response)

    async def get_cellular_status(self) -> dict[str, Any]:
        response = await self._send_request(
            self._build_sid_payload("call", ["modem", "get_status"], self.sid)
        )
        return dict(response)

    async def get_modem_info(self) -> dict[str, Any]:
        response = await self._send_request(
            self._build_sid_payload("call", ["modem", "get_info", {}], self.sid)
        )
        return dict(response)

    async def fetch_all_clients(self) -> dict[str, Any]:
        response = await self._send_request(
            self._build_sid_payload("call", ["clients", "get_list"], self.sid)
        )
        return dict(response)

    async def get_online_clients(self) -> dict[str, dict[str, Any]]:
        clients: dict[str, dict[str, Any]] = {}
        all_clients = await self.fetch_all_clients()
        for client in all_clients.get("clients", []):
            if client.get("online") is True:
                clients[str(client["mac"])] = dict(client)
        return clients

    async def clear_client_cache(self) -> dict[str, Any]:
        response = await self._send_request(
            self._build_sid_payload("call", ["clients", "clear_cache"], self.sid)
        )
        return dict(response)

    async def get_sms_messages(self) -> list[dict[str, Any]]:
        response = await self._send_request(
            self._build_sid_payload("call", ["modem", "get_sms_list", {}], self.sid)
        )
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
        response = await self._send_request(
            self._build_sid_payload(
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
                self.sid,
            ),
            timeout_seconds=max(LONG_TIMEOUT, timeout + 2),
        )
        return dict(response)

    async def remove_sms(
        self, bus: str, scope: int, message_id: str | None = None
    ) -> dict[str, Any]:
        params = {"bus": bus, "scope": scope}
        if message_id:
            params["name"] = message_id
        response = await self._send_request(
            self._build_sid_payload(
                "call",
                ["modem", "remove_sms", params],
                self.sid,
            )
        )
        return dict(response)

    async def _fetch_wifi_config(self) -> dict[str, Any]:
        response = await self._send_request(
            self._build_sid_payload("call", ["wifi", "get_config"], self.sid)
        )
        return dict(response)

    async def _apply_wifi_config(self, config: dict[str, Any]) -> dict[str, Any]:
        response = await self._send_request(
            self._build_sid_payload("call", ["wifi", "set_config", config], self.sid)
        )
        return dict(response)

    async def get_wifi_interfaces(self, redact_keys: bool = True) -> dict[str, dict[str, Any]]:
        wifi_config = await self._fetch_wifi_config()
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

    async def set_wifi_interface_enabled(self, iface_name: str, enabled: bool) -> dict[str, Any]:
        ifaces = await self.get_wifi_interfaces()
        if iface_name not in ifaces:
            raise ValueError("iface_name does not exist")
        return await self._apply_wifi_config({"enabled": enabled, "iface_name": iface_name})

    async def get_wireguard_clients(self) -> list[dict[str, Any]]:
        response = await self._send_request(
            self._build_sid_payload("call", ["wg-client", "get_all_config_list"], self.sid)
        )
        configs: list[dict[str, Any]] = []
        for item in dict(response).get("config_list", []):
            peers = item.get("peers", [])
            if not peers:
                continue
            for peer in peers:
                configs.append(
                    {
                        "name": f"{item['group_name']}/{peer['name']}",
                        "group_id": item["group_id"],
                        "peer_id": peer["peer_id"],
                        "tunnel_id": peer.get("tunnel_id"),
                    }
                )
        return configs

    async def get_wireguard_state(self) -> list[dict[str, Any]]:
        if self._firmware_version is None:
            await self.get_router_info()

        target_call = (
            "vpn-client"
            if self._firmware_version is not None
            and self._firmware_version >= NEW_VPN_CLIENT_VERSION
            else "wg-client"
        )
        response = await self._send_request(
            self._build_sid_payload("call", [target_call, "get_status"], self.sid)
        )

        if self._firmware_version is not None and self._firmware_version < NEW_VPN_CLIENT_VERSION:
            return [dict(response)]
        return [dict(item) for item in dict(response).get("status_list", [])]

    async def start_wireguard_client(self, group_id: int, peer_or_tunnel_id: int) -> dict[str, Any]:
        return await self._toggle_wireguard_client(group_id, peer_or_tunnel_id, True)

    async def stop_wireguard_client(self, peer_or_tunnel_id: int) -> dict[str, Any]:
        return await self._toggle_wireguard_client(-1, peer_or_tunnel_id, False)

    async def _toggle_wireguard_client(
        self, group_id: int, peer_or_tunnel_id: int, enabled: bool
    ) -> dict[str, Any]:
        if self._firmware_version is None:
            await self.get_router_info()

        if self._firmware_version is not None and self._firmware_version >= NEW_VPN_CLIENT_VERSION:
            response = await self._send_request(
                self._build_sid_payload(
                    "call",
                    [
                        "vpn-client",
                        "set_tunnel",
                        {"enabled": enabled, "tunnel_id": peer_or_tunnel_id},
                    ],
                    self.sid,
                )
            )
            return dict(response)

        if enabled:
            response = await self._send_request(
                self._build_sid_payload(
                    "call",
                    ["wg-client", "start", {"group_id": group_id, "peer_id": peer_or_tunnel_id}],
                    self.sid,
                )
            )
            return dict(response)

        response = await self._send_request(
            self._build_sid_payload("call", ["wg-client", "stop"], self.sid)
        )
        return dict(response)

    async def _fetch_tailscale_config(self) -> dict[str, Any] | bool:
        try:
            response = await self._send_request(
                self._build_sid_payload("call", ["tailscale", "get_config"], self.sid)
            )
        except APIClientError:
            return False
        return dict(response)

    async def _update_tailscale_config(self, config_updates: dict[str, Any]) -> dict[str, Any]:
        current_config = await self._send_request(
            self._build_sid_payload("call", ["tailscale", "get_config"], self.sid)
        )
        new_config = dict(current_config) | config_updates
        response = await self._send_request(
            self._build_sid_payload("call", ["tailscale", "set_config", new_config], self.sid)
        )
        return dict(response)

    async def _get_tailscale_status(self) -> dict[str, Any] | list[Any]:
        response = await self._send_request(
            self._build_sid_payload("call", ["tailscale", "get_status"], self.sid)
        )
        if isinstance(response, list):
            return response
        return dict(response)

    async def get_tailscale_connection(self) -> TailscaleConnection:
        state = await self._get_tailscale_status()
        if isinstance(state, list) and not state:
            return TailscaleConnection.DISCONNECTED
        return TailscaleConnection(dict(state).get("status", 0))

    async def is_tailscale_configured(self) -> bool:
        try:
            status = await self._get_tailscale_status()
        except APIClientError:
            return False
        if status != []:
            return True
        return await self._fetch_tailscale_config() is not False

    async def get_tailscale_details(self) -> dict[str, Any] | None:
        if not await self.is_tailscale_configured():
            return None
        config = await self._fetch_tailscale_config()
        return {
            "config": dict(config) if isinstance(config, dict) else {},
            "connection": await self.get_tailscale_connection(),
        }

    async def connect_tailscale(self, depth: int = 0) -> bool:
        if depth > 10:
            raise ConnectionError("Tailscale attempted to connect 10 times with no success")
        response = await self._get_tailscale_status()
        if isinstance(response, list) and response == []:
            await self._update_tailscale_config({"enabled": True})
            if depth > 0:
                await asyncio.sleep(0.3)
            return await self.connect_tailscale(depth + 1)
        status = dict(response).get("status", 0)
        if status == TailscaleConnection.CONNECTED.value:
            return True
        if status == TailscaleConnection.CONNECTING.value:
            await asyncio.sleep(3)
            latest = await self._get_tailscale_status()
            latest_status = dict(latest).get("status", 0) if isinstance(latest, dict) else 0
            if latest_status != TailscaleConnection.CONNECTED.value:
                raise ConnectionError(
                    "Tailscale did not become connected after reporting connecting"
                )
            return True
        if status in {
            TailscaleConnection.LOGIN_REQUIRED.value,
            TailscaleConnection.AUTHORIZATION_REQUIRED.value,
        }:
            raise ConnectionAbortedError("Tailscale authorization is incomplete")
        raise ConnectionError(f"Unknown tailscale status: {status}")

    async def disconnect_tailscale(self, depth: int = 0) -> bool:
        if depth > 10:
            raise ConnectionError("Tailscale attempted to disconnect 10 times with no success")
        response = await self._get_tailscale_status()
        if isinstance(response, list) and response == []:
            return True
        status = dict(response).get("status", 0)
        if status in {
            TailscaleConnection.CONNECTED.value,
            TailscaleConnection.CONNECTING.value,
        }:
            await self._update_tailscale_config({"enabled": False})
            if depth > 0:
                await asyncio.sleep(0.3)
            return await self.disconnect_tailscale(depth + 1)
        if status in {
            TailscaleConnection.LOGIN_REQUIRED.value,
            TailscaleConnection.AUTHORIZATION_REQUIRED.value,
        }:
            raise ConnectionAbortedError("Tailscale authorization is incomplete")
        return True

    async def get_repeater_status(self) -> dict[str, Any]:
        response = await self._send_request(
            self._build_sid_payload("call", ["repeater", "get_status"], self.sid)
        )
        return dict(response)

    async def get_repeater_config(self) -> dict[str, Any]:
        response = await self._send_request(
            self._build_sid_payload("call", ["repeater", "get_config"], self.sid)
        )
        return dict(response)

    async def set_repeater_config(
        self,
        auto: bool | None = None,
        lock_band: str | None = None,
        antijam: bool | None = None,
        dfs: bool | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if auto is not None:
            params["auto"] = auto
        if lock_band is not None:
            params["lock_band"] = lock_band
        if antijam is not None:
            params["antijam"] = antijam
        if dfs is not None:
            params["dfs"] = dfs
        response = await self._send_request(
            self._build_sid_payload("call", ["repeater", "set_config", params], self.sid)
        )
        return dict(response) if response else {}

    async def scan_wifi_networks(
        self, all_band: bool = False, dfs: bool = False
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {}
        if all_band:
            params["all_band"] = True
        if dfs:
            params["dfs"] = True
        response = await self._send_request(
            self._build_sid_payload("call", ["repeater", "scan", params], self.sid),
            timeout_seconds=SCAN_TIMEOUT,
        )
        return list(dict(response).get("res", []))

    async def connect_repeater(
        self,
        ssid: str,
        key: str | None = None,
        remember: bool = True,
        bssid: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"ssid": ssid, "remember": remember}
        if key:
            params["key"] = key
        if bssid:
            params["bssid"] = bssid
        response = await self._send_request(
            self._build_sid_payload("call", ["repeater", "connect", params], self.sid),
            timeout_seconds=LONG_TIMEOUT,
        )
        return dict(response) if response else {}

    async def disconnect_repeater(self) -> dict[str, Any]:
        response = await self._send_request(
            self._build_sid_payload("call", ["repeater", "disconnect"], self.sid)
        )
        return dict(response) if response else {}

    async def get_saved_ap_list(self) -> list[dict[str, Any]]:
        response = await self._send_request(
            self._build_sid_payload("call", ["repeater", "get_saved_ap_list"], self.sid)
        )
        return list(dict(response).get("res", []))

    async def remove_saved_ap(self, ssid: str) -> dict[str, Any]:
        response = await self._send_request(
            self._build_sid_payload(
                "call", ["repeater", "remove_saved_ap", {"ssid": ssid}], self.sid
            )
        )
        return dict(response) if response else {}

    async def get_fan_status(self) -> dict[str, Any]:
        response = await self._send_request(
            self._build_sid_payload("call", ["fan", "get_status"], self.sid)
        )
        return dict(response)

    async def get_fan_config(self) -> dict[str, Any]:
        response = await self._send_request(
            self._build_sid_payload("call", ["fan", "get_config"], self.sid)
        )
        return dict(response)

    async def set_fan_config(self, temperature: int) -> dict[str, Any]:
        response = await self._send_request(
            self._build_sid_payload(
                "call", ["fan", "set_config", {"temperature": temperature}], self.sid
            )
        )
        return dict(response) if response else {}

    async def test_fan(self, test: bool = True, time: int = 10) -> dict[str, Any]:
        response = await self._send_request(
            self._build_sid_payload(
                "call", ["fan", "set_test", {"test": test, "time": time}], self.sid
            )
        )
        return dict(response) if response else {}

    @property
    def logged_in(self) -> bool:
        return self._logged_in
