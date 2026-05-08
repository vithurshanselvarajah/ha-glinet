from __future__ import annotations

from typing import TYPE_CHECKING, Any

import voluptuous as vol
from homeassistant.const import CONF_MAC
from homeassistant.core import SupportsResponse
from homeassistant.helpers import config_validation as cv

from .const import (
    ATTR_ALL_BAND,
    ATTR_BSSID,
    ATTR_DFS,
    ATTR_MESSAGE_ID,
    ATTR_PASSWORD,
    ATTR_RECIPIENT,
    ATTR_REMEMBER,
    ATTR_SCOPE,
    ATTR_SSID,
    ATTR_TEMPERATURE,
    ATTR_TEXT,
    CONF_ENABLED_FEATURES,
    DOMAIN,
    FEATURE_OPTIONS,
    FEATURE_REPEATER,
    FEATURE_SMS,
    SERVICE_CONNECT_WIFI,
    SERVICE_DISCONNECT_WIFI,
    SERVICE_GET_SAVED_NETWORKS,
    SERVICE_GET_SMS,
    SERVICE_REFRESH_SMS,
    SERVICE_REMOVE_SAVED_NETWORK,
    SERVICE_REMOVE_SMS,
    SERVICE_SCAN_WIFI,
    SERVICE_SEND_SMS,
    SERVICE_SET_FAN_TEMPERATURE,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse

    from .hub import GLinetHub


def _enabled_features_from_entry(entry: Any) -> set[str]:
    if not entry:
        return set(FEATURE_OPTIONS)

    data = getattr(entry, "data", {})
    options = getattr(entry, "options", {})
    features = options.get(CONF_ENABLED_FEATURES) or data.get(CONF_ENABLED_FEATURES)

    if features is None:
        return set(FEATURE_OPTIONS)
    return set(features)


def _ensure_feature_enabled(hub: GLinetHub, feature: str, service_name: str) -> None:
    if not hub.feature_enabled(feature):
        raise ValueError(f"{service_name} is not enabled for router {hub.device_mac}")


async def async_register_services(hass: HomeAssistant) -> None:
    entries = hass.config_entries.async_entries(DOMAIN)
    if not entries:
        return

    sms_enabled = any(FEATURE_SMS in _enabled_features_from_entry(entry) for entry in entries)
    repeater_enabled = any(
        FEATURE_REPEATER in _enabled_features_from_entry(entry) for entry in entries
    )

    async def async_set_fan_temperature(call: ServiceCall) -> None:
        hub = _get_hub(hass, call.data)
        await hub.set_fan_temperature(call.data[ATTR_TEMPERATURE])

    async def async_send_sms(call: ServiceCall) -> None:
        hub = _get_hub(hass, call.data)
        _ensure_feature_enabled(hub, FEATURE_SMS, "send_sms")
        recipient = call.data[ATTR_RECIPIENT]
        await hub.send_sms(recipient, call.data[ATTR_TEXT])

    async def async_refresh_sms(call: ServiceCall) -> None:
        hub = _get_hub(hass, call.data)
        _ensure_feature_enabled(hub, FEATURE_SMS, "refresh_sms")
        await hub.fetch_sms_messages()

    async def async_get_sms(call: ServiceCall) -> ServiceResponse:
        hub = _get_hub(hass, call.data)
        _ensure_feature_enabled(hub, FEATURE_SMS, "get_sms")
        await hub.fetch_sms_messages()
        return {
            "messages": [
                {
                    "id": msg.message_id,
                    "phone_number": msg.phone_number,
                    "direction": msg.direction.value,
                    "status": msg.status_label,
                    "text": msg.text,
                    "timestamp": msg.timestamp,
                }
                for msg in hub.sms_messages.values()
            ]
        }

    async def async_remove_sms(call: ServiceCall) -> None:
        hub = _get_hub(hass, call.data)
        _ensure_feature_enabled(hub, FEATURE_SMS, "remove_sms")
        await hub.remove_sms(
            scope=call.data[ATTR_SCOPE],
            message_id=call.data.get(ATTR_MESSAGE_ID),
        )

    if sms_enabled:
        hass.services.async_register(
            DOMAIN,
            SERVICE_SEND_SMS,
            async_send_sms,
            schema=vol.Schema(
                {
                    vol.Required(ATTR_RECIPIENT): cv.string,
                    vol.Required(ATTR_TEXT): cv.string,
                }
            ),
        )
        hass.services.async_register(
            DOMAIN,
            SERVICE_REFRESH_SMS,
            async_refresh_sms,
            schema=vol.Schema({vol.Optional(CONF_MAC): cv.string}),
        )
        hass.services.async_register(
            DOMAIN,
            SERVICE_GET_SMS,
            async_get_sms,
            schema=vol.Schema({vol.Optional(CONF_MAC): cv.string}),
            supports_response=SupportsResponse.ONLY,
        )
        hass.services.async_register(
            DOMAIN,
            SERVICE_REMOVE_SMS,
            async_remove_sms,
            schema=vol.Schema(
                {
                    vol.Optional(CONF_MAC): cv.string,
                    vol.Required(ATTR_SCOPE, default=10): vol.In(
                        [0, 1, 2, 3, 4, 5, 10, 11, 12, 13]
                    ),
                    vol.Optional(ATTR_MESSAGE_ID): cv.string,
                }
            ),
        )
    else:
        for service in [SERVICE_SEND_SMS, SERVICE_REFRESH_SMS, SERVICE_GET_SMS, SERVICE_REMOVE_SMS]:
            if hass.services.has_service(DOMAIN, service):
                hass.services.async_remove(DOMAIN, service)

    async def async_scan_wifi(call: ServiceCall) -> ServiceResponse:
        hub = _get_hub(hass, call.data)
        _ensure_feature_enabled(hub, FEATURE_REPEATER, "scan_wifi")
        networks = await hub.scan_wifi_networks(
            all_band=call.data.get(ATTR_ALL_BAND, False),
            dfs=call.data.get(ATTR_DFS, False),
        )
        return {
            "networks": [
                {
                    "ssid": network.ssid,
                    "bssid": network.bssid,
                    "signal": network.signal,
                    "band": network.band,
                    "channel": network.channel,
                    "encryption": network.encryption_type,
                    "saved": network.saved,
                }
                for network in networks
            ]
        }

    async def async_connect_wifi(call: ServiceCall) -> None:
        hub = _get_hub(hass, call.data)
        _ensure_feature_enabled(hub, FEATURE_REPEATER, "connect_wifi")
        await hub.connect_to_wifi(
            ssid=call.data[ATTR_SSID],
            password=call.data.get(ATTR_PASSWORD),
            remember=call.data.get(ATTR_REMEMBER, True),
            bssid=call.data.get(ATTR_BSSID),
        )

    async def async_disconnect_wifi(call: ServiceCall) -> None:
        hub = _get_hub(hass, call.data)
        _ensure_feature_enabled(hub, FEATURE_REPEATER, "disconnect_wifi")
        await hub.disconnect_wifi()

    async def async_get_saved_networks(call: ServiceCall) -> ServiceResponse:
        hub = _get_hub(hass, call.data)
        _ensure_feature_enabled(hub, FEATURE_REPEATER, "get_saved_networks")
        networks = await hub.get_saved_wifi_networks()
        return {
            "networks": [
                {
                    "ssid": network.get("ssid"),
                    "bssid": network.get("bssid"),
                    "protocol": network.get("protocol", "dhcp"),
                }
                for network in networks
            ]
        }

    async def async_remove_saved_network(call: ServiceCall) -> None:
        hub = _get_hub(hass, call.data)
        _ensure_feature_enabled(hub, FEATURE_REPEATER, "remove_saved_network")
        await hub.remove_saved_wifi_network(call.data[ATTR_SSID])

    if repeater_enabled:
        hass.services.async_register(
            DOMAIN,
            SERVICE_SCAN_WIFI,
            async_scan_wifi,
            schema=vol.Schema(
                {
                    vol.Optional(CONF_MAC): cv.string,
                    vol.Optional(ATTR_ALL_BAND, default=False): cv.boolean,
                    vol.Optional(ATTR_DFS, default=False): cv.boolean,
                }
            ),
            supports_response=SupportsResponse.ONLY,
        )
        hass.services.async_register(
            DOMAIN,
            SERVICE_CONNECT_WIFI,
            async_connect_wifi,
            schema=vol.Schema(
                {
                    vol.Optional(CONF_MAC): cv.string,
                    vol.Required(ATTR_SSID): cv.string,
                    vol.Optional(ATTR_PASSWORD): cv.string,
                    vol.Optional(ATTR_REMEMBER, default=True): cv.boolean,
                    vol.Optional(ATTR_BSSID): cv.string,
                }
            ),
        )
        hass.services.async_register(
            DOMAIN,
            SERVICE_DISCONNECT_WIFI,
            async_disconnect_wifi,
            schema=vol.Schema({vol.Optional(CONF_MAC): cv.string}),
        )
        hass.services.async_register(
            DOMAIN,
            SERVICE_GET_SAVED_NETWORKS,
            async_get_saved_networks,
            schema=vol.Schema({vol.Optional(CONF_MAC): cv.string}),
            supports_response=SupportsResponse.ONLY,
        )
        hass.services.async_register(
            DOMAIN,
            SERVICE_REMOVE_SAVED_NETWORK,
            async_remove_saved_network,
            schema=vol.Schema(
                {
                    vol.Optional(CONF_MAC): cv.string,
                    vol.Required(ATTR_SSID): cv.string,
                }
            ),
        )
    else:
        for service in [
            SERVICE_SCAN_WIFI,
            SERVICE_CONNECT_WIFI,
            SERVICE_DISCONNECT_WIFI,
            SERVICE_GET_SAVED_NETWORKS,
            SERVICE_REMOVE_SAVED_NETWORK,
        ]:
            if hass.services.has_service(DOMAIN, service):
                hass.services.async_remove(DOMAIN, service)

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_FAN_TEMPERATURE,
        async_set_fan_temperature,
        schema=vol.Schema(
            {
                vol.Optional(CONF_MAC): cv.string,
                vol.Required(ATTR_TEMPERATURE): vol.All(
                    vol.Coerce(int), vol.Range(min=40, max=100)
                ),
            }
        ),
    )


def _get_hub(hass: HomeAssistant, call_data: dict[str, Any]) -> GLinetHub:
    entries = hass.config_entries.async_entries(DOMAIN)
    if not entries:
        raise ValueError("No GL-INet config entries are loaded")

    target_mac = call_data.get(CONF_MAC)
    for config_entry in entries:
        hub: GLinetHub | None = getattr(config_entry, "runtime_data", None)
        if hub is None:
            continue
        if target_mac is None or hub.device_mac.lower() == str(target_mac).lower():
            return hub
    raise ValueError(f"No GL-INet router found for MAC address {target_mac}")
