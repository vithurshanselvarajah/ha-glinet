from __future__ import annotations

from typing import TYPE_CHECKING, Any

import voluptuous as vol
from homeassistant.const import CONF_MAC
from homeassistant.core import SupportsResponse
from homeassistant.helpers import config_validation as cv

from .const import (
    ATTR_ALL_BAND,
    ATTR_BLOCK,
    ATTR_BODY,
    ATTR_BSSID,
    ATTR_CONFIG,
    ATTR_CAPACITY,
    ATTR_CAPACITY_ENABLED,
    ATTR_CONTENT,
    ATTR_CUSTOM,
    ATTR_DEST,
    ATTR_DEST_IP,
    ATTR_DEST_PORT,
    ATTR_DFS,
    ATTR_DURATION,
    ATTR_ENABLED,
    ATTR_INTERFACE,
    ATTR_GROUP_ID,
    ATTR_LAN,
    ATTR_MAIN,
    ATTR_MESSAGE_ID,
    ATTR_METHOD,
    ATTR_MODE,
    ATTR_SENSITIVITY,
    ATTR_NAME,
    ATTR_PASSWORD,
    ATTR_PROTO,
    ATTR_RECIPIENT,
    ATTR_REFRESH,
    ATTR_REMEMBER,
    ATTR_REMOVE_ALL,
    ATTR_RULE_ID,
    ATTR_SCOPE,
    ATTR_SRC,
    ATTR_SRC_DPORT,
    ATTR_SRC_IP,
    ATTR_SRC_MAC,
    ATTR_SRC_PORT,
    ATTR_SSID,
    ATTR_TARGET,
    ATTR_TEMP_HIGH,
    ATTR_TEMP_HIGH_ENABLED,
    ATTR_TEMP_LOW,
    ATTR_TEMP_LOW_ENABLED,
    ATTR_TEMPERATURE,
    ATTR_TEXT,
    ATTR_VPN,
    ATTR_WIFI_2G,
    ATTR_WIFI_5G,
    ATTR_WIFI_PASSWORD,
    CONF_ENABLED_FEATURES,
    DOMAIN,
    FEATURE_FIREWALL,
    FEATURE_KMWAN,
    FEATURE_MWAN3,
    FEATURE_MCU_BATTERY,
    FEATURE_MCU_OLED,
    FEATURE_OPTIONS,
    FEATURE_PARENTAL_CONTROL,
    FEATURE_PLAYGROUND,
    FEATURE_REPEATER,
    FEATURE_SMS,
    SERVICE_ACCESS_CONTROL_SET_DEVICE_BLOCK,
    SERVICE_ACCESS_CONTROL_SET_MODE,
    SERVICE_ADD_FIREWALL_RULE,
    SERVICE_ADD_PORT_FORWARD,
    SERVICE_CONNECT_WIFI,
    SERVICE_DISCONNECT_WIFI,
    SERVICE_GET_FIREWALL_RULES,
    SERVICE_GET_MCU_BATTERY_CONFIG,
    SERVICE_GET_MCU_OLED_CONFIG,
    SERVICE_GET_SAVED_NETWORKS,
    SERVICE_GET_SMS,
    SERVICE_KMWAN_GET_CONFIG,
    SERVICE_KMWAN_GET_STATUS,
    SERVICE_KMWAN_SET_CONFIG,
    SERVICE_KMWAN_SET_INTERFACE,
    SERVICE_KMWAN_SET_SENSITIVITY,
    SERVICE_MWAN3_GET_CONFIG,
    SERVICE_MWAN3_GET_STATUS,
    SERVICE_MWAN3_SET_CONFIG,
    SERVICE_MWAN3_SET_INTERFACE,
    SERVICE_PARENTAL_CONTROL_SET_FILTERING_MODE,
    SERVICE_PARENTAL_CONTROL_SET_GROUP_SCHEDULES,
    SERVICE_PARENTAL_CONTROL_SET_TEMPORARY_OVERRIDE,
    SERVICE_PARENTAL_CONTROL_UPDATE_SIGNATURES,
    SERVICE_PLAYGROUND,
    SERVICE_REFRESH_SMS,
    SERVICE_REMOVE_FIREWALL_RULE,
    SERVICE_REMOVE_PORT_FORWARD,
    SERVICE_REMOVE_SAVED_NETWORK,
    SERVICE_REMOVE_SMS,
    SERVICE_SCAN_WIFI,
    SERVICE_SEND_SMS,
    SERVICE_SET_DMZ,
    SERVICE_SET_FAN_TEMPERATURE,
    SERVICE_SET_MCU_BATTERY_CONFIG,
    SERVICE_SET_MCU_OLED_CONFIG,
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

    firewall_enabled = any(
        FEATURE_FIREWALL in _enabled_features_from_entry(entry) for entry in entries
    )
    mwan3_enabled = any(
        FEATURE_MWAN3 in _enabled_features_from_entry(entry) for entry in entries
    )
    kmwan_enabled = any(
        FEATURE_KMWAN in _enabled_features_from_entry(entry) for entry in entries
    )
    mcu_battery_enabled = any(
        FEATURE_MCU_BATTERY in _enabled_features_from_entry(entry) for entry in entries
    )
    mcu_oled_enabled = any(
        FEATURE_MCU_OLED in _enabled_features_from_entry(entry) for entry in entries
    )
    sms_enabled = any(FEATURE_SMS in _enabled_features_from_entry(entry) for entry in entries)
    repeater_enabled = any(
        FEATURE_REPEATER in _enabled_features_from_entry(entry) for entry in entries
    )
    parental_control_enabled = any(
        FEATURE_PARENTAL_CONTROL in _enabled_features_from_entry(entry)
        for entry in entries
    )
    playground_enabled = any(
        FEATURE_PLAYGROUND in _enabled_features_from_entry(entry) for entry in entries
    )

    async def async_set_fan_temperature(call: ServiceCall) -> None:
        hub = _get_hub(hass, call.data)
        await hub.set_fan_temperature(call.data[ATTR_TEMPERATURE])

    async def async_mwan3_get_config(call: ServiceCall) -> ServiceResponse:
        hub = _get_hub(hass, call.data)
        _ensure_feature_enabled(hub, FEATURE_MWAN3, SERVICE_MWAN3_GET_CONFIG)
        return {"config": await hub.get_mwan3_config()}

    async def async_mwan3_get_status(call: ServiceCall) -> ServiceResponse:
        hub = _get_hub(hass, call.data)
        _ensure_feature_enabled(hub, FEATURE_MWAN3, SERVICE_MWAN3_GET_STATUS)
        return {"status": await hub.get_mwan3_status()}

    async def async_mwan3_set_config(call: ServiceCall) -> None:
        hub = _get_hub(hass, call.data)
        _ensure_feature_enabled(hub, FEATURE_MWAN3, SERVICE_MWAN3_SET_CONFIG)
        await hub.set_mwan3_config(dict(call.data[ATTR_CONFIG]))

    async def async_mwan3_set_interface(call: ServiceCall) -> None:
        hub = _get_hub(hass, call.data)
        _ensure_feature_enabled(hub, FEATURE_MWAN3, SERVICE_MWAN3_SET_INTERFACE)
        await hub.set_mwan3_interface(dict(call.data[ATTR_INTERFACE]))

    async def async_kmwan_get_config(call: ServiceCall) -> ServiceResponse:
        hub = _get_hub(hass, call.data)
        _ensure_feature_enabled(hub, FEATURE_KMWAN, SERVICE_KMWAN_GET_CONFIG)
        return {"config": await hub.get_kmwan_config()}

    async def async_kmwan_get_status(call: ServiceCall) -> ServiceResponse:
        hub = _get_hub(hass, call.data)
        _ensure_feature_enabled(hub, FEATURE_KMWAN, SERVICE_KMWAN_GET_STATUS)
        return {"status": await hub.get_kmwan_status()}

    async def async_kmwan_set_config(call: ServiceCall) -> None:
        hub = _get_hub(hass, call.data)
        _ensure_feature_enabled(hub, FEATURE_KMWAN, SERVICE_KMWAN_SET_CONFIG)
        await hub.set_kmwan_config(dict(call.data[ATTR_CONFIG]))

    async def async_kmwan_set_interface(call: ServiceCall) -> None:
        hub = _get_hub(hass, call.data)
        _ensure_feature_enabled(hub, FEATURE_KMWAN, SERVICE_KMWAN_SET_INTERFACE)
        await hub.set_kmwan_interface(dict(call.data[ATTR_INTERFACE]))

    async def async_kmwan_set_sensitivity(call: ServiceCall) -> None:
        hub = _get_hub(hass, call.data)
        _ensure_feature_enabled(hub, FEATURE_KMWAN, SERVICE_KMWAN_SET_SENSITIVITY)
        await hub.set_kmwan_sensitivity(dict(call.data[ATTR_SENSITIVITY]))

    async def async_playground(call: ServiceCall) -> ServiceResponse:
        hub = _get_hub(hass, call.data)
        _ensure_feature_enabled(hub, FEATURE_PLAYGROUND, SERVICE_PLAYGROUND)
        method = call.data[ATTR_METHOD]
        body = call.data.get(ATTR_BODY)
        response = await hub.custom_request(method, body)
        if response is None:
            return {"error": "API invocation failed"}
        if isinstance(response, dict):
            return response
        return {"result": response}

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

    async def async_add_firewall_rule(call: ServiceCall) -> None:
        hub = _get_hub(hass, call.data)
        _ensure_feature_enabled(hub, FEATURE_FIREWALL, "add_firewall_rule")
        params = {k: v for k, v in call.data.items() if k != CONF_MAC}
        await hub.add_firewall_rule(params)

    async def async_remove_firewall_rule(call: ServiceCall) -> None:
        hub = _get_hub(hass, call.data)
        _ensure_feature_enabled(hub, FEATURE_FIREWALL, "remove_firewall_rule")
        await hub.remove_firewall_rule(rule_id=call.data[ATTR_RULE_ID])

    async def async_get_firewall_rules(call: ServiceCall) -> ServiceResponse:
        hub = _get_hub(hass, call.data)
        _ensure_feature_enabled(hub, FEATURE_FIREWALL, "get_firewall_rules")
        return {"rules": await hub.get_firewall_rule_summaries()}

    async def async_add_port_forward(call: ServiceCall) -> None:
        hub = _get_hub(hass, call.data)
        _ensure_feature_enabled(hub, FEATURE_FIREWALL, "add_port_forward")
        params = {k: v for k, v in call.data.items() if k != CONF_MAC}
        await hub.add_port_forward(params)

    async def async_remove_port_forward(call: ServiceCall) -> None:
        hub = _get_hub(hass, call.data)
        _ensure_feature_enabled(hub, FEATURE_FIREWALL, "remove_port_forward")
        await hub.remove_port_forward(
            rule_id=call.data.get(ATTR_RULE_ID),
            remove_all=call.data.get(ATTR_REMOVE_ALL, False),
        )

    async def async_set_dmz(call: ServiceCall) -> None:
        hub = _get_hub(hass, call.data)
        _ensure_feature_enabled(hub, FEATURE_FIREWALL, "set_dmz")
        await hub.set_dmz_config(
            enabled=call.data[ATTR_ENABLED],
            dest_ip=call.data.get(ATTR_DEST_IP),
        )

    async def async_get_mcu_battery_config(call: ServiceCall) -> ServiceResponse:
        hub = _get_hub(hass, call.data)
        _ensure_feature_enabled(hub, FEATURE_MCU_BATTERY, "get_mcu_battery_config")
        return {"config": await hub.get_mcu_battery_config()}

    async def async_set_mcu_battery_config(call: ServiceCall) -> None:
        hub = _get_hub(hass, call.data)
        _ensure_feature_enabled(hub, FEATURE_MCU_BATTERY, "set_mcu_battery_config")
        config = {
            "capacity": {
                "enable": call.data[ATTR_CAPACITY_ENABLED],
                "value": call.data[ATTR_CAPACITY],
            },
            "temp_high": {
                "enable": call.data[ATTR_TEMP_HIGH_ENABLED],
                "value": call.data[ATTR_TEMP_HIGH],
            },
            "temp_low": {
                "enable": call.data[ATTR_TEMP_LOW_ENABLED],
                "value": call.data[ATTR_TEMP_LOW],
            },
        }
        await hub.set_mcu_battery_config(config)

    async def async_get_mcu_oled_config(call: ServiceCall) -> ServiceResponse:
        hub = _get_hub(hass, call.data)
        _ensure_feature_enabled(hub, FEATURE_MCU_OLED, "get_mcu_oled_config")
        return {"config": await hub.get_mcu_oled_config()}

    async def async_set_mcu_oled_config(call: ServiceCall) -> None:
        hub = _get_hub(hass, call.data)
        _ensure_feature_enabled(hub, FEATURE_MCU_OLED, "set_mcu_oled_config")
        screen_display = {
            key: call.data[key]
            for key in (
                ATTR_MAIN,
                ATTR_WIFI_PASSWORD,
                ATTR_WIFI_2G,
                ATTR_WIFI_5G,
                ATTR_LAN,
                ATTR_VPN,
                ATTR_CUSTOM,
                ATTR_CONTENT,
            )
            if key in call.data
        }
        await hub.set_mcu_oled_config(screen_display)

    async def async_parental_control_set_temporary_override(
        call: ServiceCall,
    ) -> None:
        hub = _get_hub(hass, call.data)
        _ensure_feature_enabled(
            hub,
            FEATURE_PARENTAL_CONTROL,
            "parental_control_set_temporary_override",
        )
        await hub.set_temporary_override(
            group_id=call.data[ATTR_GROUP_ID],
            enable=call.data[ATTR_ENABLED],
            duration=call.data.get(ATTR_DURATION, ""),
            rule_id=call.data[ATTR_RULE_ID],
        )

    async def async_parental_control_set_filtering_mode(call: ServiceCall) -> None:
        hub = _get_hub(hass, call.data)
        _ensure_feature_enabled(
            hub,
            FEATURE_PARENTAL_CONTROL,
            "parental_control_set_filtering_mode",
        )
        await hub.set_parental_mode(call.data[ATTR_MODE])

    async def async_parental_control_update_signatures(call: ServiceCall) -> None:
        hub = _get_hub(hass, call.data)
        _ensure_feature_enabled(
            hub,
            FEATURE_PARENTAL_CONTROL,
            "parental_control_update_signatures",
        )
        await hub.update_parental_signatures()

    async def async_access_control_set_mode(call: ServiceCall) -> None:
        hub = _get_hub(hass, call.data)
        _ensure_feature_enabled(hub, FEATURE_PARENTAL_CONTROL, "access_control_set_mode")
        await hub.set_access_control_mode(call.data[ATTR_MODE])

    async def async_access_control_set_device_block(call: ServiceCall) -> None:
        hub = _get_hub(hass, call.data)
        _ensure_feature_enabled(
            hub,
            FEATURE_PARENTAL_CONTROL,
            "access_control_set_device_block",
        )
        await hub.set_single_device_block(call.data[ATTR_SRC_MAC], call.data[ATTR_BLOCK])

    async def async_parental_control_set_group_schedules(call: ServiceCall) -> None:
        hub = _get_hub(hass, call.data)
        _ensure_feature_enabled(
            hub,
            FEATURE_PARENTAL_CONTROL,
            "parental_control_set_group_schedules",
        )
        await hub.set_group_schedules_enabled(
            call.data[ATTR_GROUP_ID],
            call.data[ATTR_ENABLED],
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
            refresh=call.data.get(ATTR_REFRESH, False),
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
                    vol.Optional(ATTR_REFRESH, default=False): cv.boolean,
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

    if firewall_enabled:
        hass.services.async_register(
            DOMAIN,
            SERVICE_ADD_FIREWALL_RULE,
            async_add_firewall_rule,
            schema=vol.Schema(
                {
                    vol.Optional(CONF_MAC): cv.string,
                    vol.Required(ATTR_NAME): cv.string,
                    vol.Required(ATTR_SRC): cv.string,
                    vol.Optional(ATTR_SRC_IP): cv.string,
                    vol.Optional(ATTR_SRC_MAC): cv.string,
                    vol.Optional(ATTR_SRC_PORT): cv.string,
                    vol.Required(ATTR_PROTO): cv.string,
                    vol.Required(ATTR_DEST): cv.string,
                    vol.Optional(ATTR_DEST_IP): cv.string,
                    vol.Optional(ATTR_DEST_PORT): cv.string,
                    vol.Required(ATTR_TARGET): cv.string,
                    vol.Optional(ATTR_ENABLED, default=True): cv.boolean,
                }
            ),
        )
        hass.services.async_register(
            DOMAIN,
            SERVICE_GET_FIREWALL_RULES,
            async_get_firewall_rules,
            schema=vol.Schema({vol.Optional(CONF_MAC): cv.string}),
            supports_response=SupportsResponse.ONLY,
        )
        hass.services.async_register(
            DOMAIN,
            SERVICE_REMOVE_FIREWALL_RULE,
            async_remove_firewall_rule,
            schema=vol.Schema(
                {
                    vol.Optional(CONF_MAC): cv.string,
                    vol.Required(ATTR_RULE_ID): cv.string,
                }
            ),
        )
        hass.services.async_register(
            DOMAIN,
            SERVICE_ADD_PORT_FORWARD,
            async_add_port_forward,
            schema=vol.Schema(
                {
                    vol.Optional(CONF_MAC): cv.string,
                    vol.Required(ATTR_NAME): cv.string,
                    vol.Required(ATTR_SRC): cv.string,
                    vol.Required(ATTR_SRC_DPORT): cv.string,
                    vol.Required(ATTR_PROTO): cv.string,
                    vol.Required(ATTR_DEST): cv.string,
                    vol.Required(ATTR_DEST_IP): cv.string,
                    vol.Required(ATTR_DEST_PORT): cv.string,
                    vol.Optional(ATTR_ENABLED, default=True): cv.boolean,
                }
            ),
        )
        hass.services.async_register(
            DOMAIN,
            SERVICE_REMOVE_PORT_FORWARD,
            async_remove_port_forward,
            schema=vol.Schema(
                {
                    vol.Optional(CONF_MAC): cv.string,
                    vol.Optional(ATTR_RULE_ID): cv.string,
                    vol.Optional(ATTR_REMOVE_ALL, default=False): cv.boolean,
                }
            ),
        )
        hass.services.async_register(
            DOMAIN,
            SERVICE_SET_DMZ,
            async_set_dmz,
            schema=vol.Schema(
                {
                    vol.Optional(CONF_MAC): cv.string,
                    vol.Required(ATTR_ENABLED): cv.boolean,
                    vol.Optional(ATTR_DEST_IP): cv.string,
                }
            ),
        )
    else:
        for service in [
            SERVICE_ADD_FIREWALL_RULE,
            SERVICE_GET_FIREWALL_RULES,
            SERVICE_REMOVE_FIREWALL_RULE,
            SERVICE_ADD_PORT_FORWARD,
            SERVICE_REMOVE_PORT_FORWARD,
            SERVICE_SET_DMZ,
        ]:
            if hass.services.has_service(DOMAIN, service):
                hass.services.async_remove(DOMAIN, service)

    if kmwan_enabled:
        hass.services.async_register(
            DOMAIN,
            SERVICE_KMWAN_GET_CONFIG,
            async_kmwan_get_config,
            schema=vol.Schema({vol.Optional(CONF_MAC): cv.string}),
            supports_response=SupportsResponse.ONLY,
        )
        hass.services.async_register(
            DOMAIN,
            SERVICE_KMWAN_GET_STATUS,
            async_kmwan_get_status,
            schema=vol.Schema({vol.Optional(CONF_MAC): cv.string}),
            supports_response=SupportsResponse.ONLY,
        )
        hass.services.async_register(
            DOMAIN,
            SERVICE_KMWAN_SET_CONFIG,
            async_kmwan_set_config,
            schema=vol.Schema(
                {
                    vol.Optional(CONF_MAC): cv.string,
                    vol.Required(ATTR_CONFIG): object,
                }
            ),
        )
        hass.services.async_register(
            DOMAIN,
            SERVICE_KMWAN_SET_INTERFACE,
            async_kmwan_set_interface,
            schema=vol.Schema(
                {
                    vol.Optional(CONF_MAC): cv.string,
                    vol.Required(ATTR_INTERFACE): object,
                }
            ),
        )
        hass.services.async_register(
            DOMAIN,
            SERVICE_KMWAN_SET_SENSITIVITY,
            async_kmwan_set_sensitivity,
            schema=vol.Schema(
                {
                    vol.Optional(CONF_MAC): cv.string,
                    vol.Required(ATTR_SENSITIVITY): object,
                }
            ),
        )
    else:
        for service in [
            SERVICE_KMWAN_GET_CONFIG,
            SERVICE_KMWAN_GET_STATUS,
            SERVICE_KMWAN_SET_CONFIG,
            SERVICE_KMWAN_SET_INTERFACE,
            SERVICE_KMWAN_SET_SENSITIVITY,
        ]:
            if hass.services.has_service(DOMAIN, service):
                hass.services.async_remove(DOMAIN, service)

    if mwan3_enabled:
        hass.services.async_register(
            DOMAIN,
            SERVICE_MWAN3_GET_CONFIG,
            async_mwan3_get_config,
            schema=vol.Schema({vol.Optional(CONF_MAC): cv.string}),
            supports_response=SupportsResponse.ONLY,
        )
        hass.services.async_register(
            DOMAIN,
            SERVICE_MWAN3_GET_STATUS,
            async_mwan3_get_status,
            schema=vol.Schema({vol.Optional(CONF_MAC): cv.string}),
            supports_response=SupportsResponse.ONLY,
        )
        hass.services.async_register(
            DOMAIN,
            SERVICE_MWAN3_SET_CONFIG,
            async_mwan3_set_config,
            schema=vol.Schema(
                {
                    vol.Optional(CONF_MAC): cv.string,
                    vol.Required(ATTR_CONFIG): object,
                }
            ),
        )
        hass.services.async_register(
            DOMAIN,
            SERVICE_MWAN3_SET_INTERFACE,
            async_mwan3_set_interface,
            schema=vol.Schema(
                {
                    vol.Optional(CONF_MAC): cv.string,
                    vol.Required(ATTR_INTERFACE): object,
                }
            ),
        )
    else:
        for service in [
            SERVICE_MWAN3_GET_CONFIG,
            SERVICE_MWAN3_GET_STATUS,
            SERVICE_MWAN3_SET_CONFIG,
            SERVICE_MWAN3_SET_INTERFACE,
        ]:
            if hass.services.has_service(DOMAIN, service):
                hass.services.async_remove(DOMAIN, service)

    if mcu_battery_enabled:
        hass.services.async_register(
            DOMAIN,
            SERVICE_GET_MCU_BATTERY_CONFIG,
            async_get_mcu_battery_config,
            schema=vol.Schema({vol.Optional(CONF_MAC): cv.string}),
            supports_response=SupportsResponse.ONLY,
        )
        hass.services.async_register(
            DOMAIN,
            SERVICE_SET_MCU_BATTERY_CONFIG,
            async_set_mcu_battery_config,
            schema=vol.Schema(
                {
                    vol.Optional(CONF_MAC): cv.string,
                    vol.Required(ATTR_CAPACITY_ENABLED): cv.boolean,
                    vol.Required(ATTR_CAPACITY): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=100)
                    ),
                    vol.Required(ATTR_TEMP_HIGH_ENABLED): cv.boolean,
                    vol.Required(ATTR_TEMP_HIGH): vol.Coerce(int),
                    vol.Required(ATTR_TEMP_LOW_ENABLED): cv.boolean,
                    vol.Required(ATTR_TEMP_LOW): vol.Coerce(int),
                }
            ),
        )
    else:
        for service in [
            SERVICE_GET_MCU_BATTERY_CONFIG,
            SERVICE_SET_MCU_BATTERY_CONFIG,
        ]:
            if hass.services.has_service(DOMAIN, service):
                hass.services.async_remove(DOMAIN, service)

    if mcu_oled_enabled:
        hass.services.async_register(
            DOMAIN,
            SERVICE_GET_MCU_OLED_CONFIG,
            async_get_mcu_oled_config,
            schema=vol.Schema({vol.Optional(CONF_MAC): cv.string}),
            supports_response=SupportsResponse.ONLY,
        )
        hass.services.async_register(
            DOMAIN,
            SERVICE_SET_MCU_OLED_CONFIG,
            async_set_mcu_oled_config,
            schema=vol.Schema(
                {
                    vol.Optional(CONF_MAC): cv.string,
                    vol.Optional(ATTR_MAIN): cv.boolean,
                    vol.Optional(ATTR_WIFI_PASSWORD): cv.boolean,
                    vol.Optional(ATTR_WIFI_2G): cv.boolean,
                    vol.Optional(ATTR_WIFI_5G): cv.boolean,
                    vol.Optional(ATTR_LAN): cv.boolean,
                    vol.Optional(ATTR_VPN): cv.boolean,
                    vol.Optional(ATTR_CUSTOM): cv.boolean,
                    vol.Optional(ATTR_CONTENT): cv.string,
                }
            ),
        )
    else:
        for service in [
            SERVICE_GET_MCU_OLED_CONFIG,
            SERVICE_SET_MCU_OLED_CONFIG,
        ]:
            if hass.services.has_service(DOMAIN, service):
                hass.services.async_remove(DOMAIN, service)

    if parental_control_enabled:
        hass.services.async_register(
            DOMAIN,
            SERVICE_PARENTAL_CONTROL_SET_TEMPORARY_OVERRIDE,
            async_parental_control_set_temporary_override,
            schema=vol.Schema(
                {
                    vol.Optional(CONF_MAC): cv.string,
                    vol.Required(ATTR_GROUP_ID): cv.string,
                    vol.Required(ATTR_ENABLED): cv.boolean,
                    vol.Required(ATTR_RULE_ID): cv.string,
                    vol.Optional(ATTR_DURATION, default=""): cv.string,
                }
            ),
        )
        hass.services.async_register(
            DOMAIN,
            SERVICE_PARENTAL_CONTROL_SET_FILTERING_MODE,
            async_parental_control_set_filtering_mode,
            schema=vol.Schema(
                {
                    vol.Optional(CONF_MAC): cv.string,
                    vol.Required(ATTR_MODE): vol.Coerce(int),
                }
            ),
        )
        hass.services.async_register(
            DOMAIN,
            SERVICE_PARENTAL_CONTROL_UPDATE_SIGNATURES,
            async_parental_control_update_signatures,
            schema=vol.Schema({vol.Optional(CONF_MAC): cv.string}),
        )
        hass.services.async_register(
            DOMAIN,
            SERVICE_ACCESS_CONTROL_SET_MODE,
            async_access_control_set_mode,
            schema=vol.Schema(
                {
                    vol.Optional(CONF_MAC): cv.string,
                    vol.Required(ATTR_MODE): vol.In(["black", "white"]),
                }
            ),
        )
        hass.services.async_register(
            DOMAIN,
            SERVICE_ACCESS_CONTROL_SET_DEVICE_BLOCK,
            async_access_control_set_device_block,
            schema=vol.Schema(
                {
                    vol.Optional(CONF_MAC): cv.string,
                    vol.Required(ATTR_SRC_MAC): cv.string,
                    vol.Required(ATTR_BLOCK): cv.boolean,
                }
            ),
        )
        hass.services.async_register(
            DOMAIN,
            SERVICE_PARENTAL_CONTROL_SET_GROUP_SCHEDULES,
            async_parental_control_set_group_schedules,
            schema=vol.Schema(
                {
                    vol.Optional(CONF_MAC): cv.string,
                    vol.Required(ATTR_GROUP_ID): cv.string,
                    vol.Required(ATTR_ENABLED): cv.boolean,
                }
            ),
        )
    else:
        for service in [
            SERVICE_PARENTAL_CONTROL_SET_TEMPORARY_OVERRIDE,
            SERVICE_PARENTAL_CONTROL_SET_FILTERING_MODE,
            SERVICE_PARENTAL_CONTROL_UPDATE_SIGNATURES,
            SERVICE_ACCESS_CONTROL_SET_MODE,
            SERVICE_ACCESS_CONTROL_SET_DEVICE_BLOCK,
            SERVICE_PARENTAL_CONTROL_SET_GROUP_SCHEDULES,
        ]:
            if hass.services.has_service(DOMAIN, service):
                hass.services.async_remove(DOMAIN, service)

    if playground_enabled:
        hass.services.async_register(
            DOMAIN,
            SERVICE_PLAYGROUND,
            async_playground,
            schema=vol.Schema(
                {
                    vol.Optional(CONF_MAC): cv.string,
                    vol.Required(ATTR_METHOD): cv.string,
                    vol.Optional(ATTR_BODY): object,
                }
            ),
            supports_response=SupportsResponse.ONLY,
        )
    else:
        if hass.services.has_service(DOMAIN, SERVICE_PLAYGROUND):
            hass.services.async_remove(DOMAIN, SERVICE_PLAYGROUND)

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_FAN_TEMPERATURE,
        async_set_fan_temperature,
        schema=vol.Schema(
            {
                vol.Optional(CONF_MAC): cv.string,
                vol.Required(ATTR_TEMPERATURE): vol.All(
                    vol.Coerce(int), vol.Range(min=70, max=90)
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
