from __future__ import annotations

from typing import TYPE_CHECKING, Any

import voluptuous as vol
from homeassistant.const import CONF_MAC
from homeassistant.core import SupportsResponse
from homeassistant.helpers import config_validation as cv

from .const import (
    ATTR_MESSAGE_ID,
    ATTR_RECIPIENT,
    ATTR_SCOPE,
    ATTR_TEXT,
    DOMAIN,
    SERVICE_GET_SMS,
    SERVICE_REFRESH_SMS,
    SERVICE_REMOVE_SMS,
    SERVICE_SEND_SMS,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse

    from .hub import GLinetHub


async def async_register_services(hass: HomeAssistant) -> None:
    if hass.services.has_service(DOMAIN, SERVICE_SEND_SMS):
        return

    async def async_send_sms(call: ServiceCall) -> None:
        hub = _get_hub(hass, call.data)
        recipient = call.data[ATTR_RECIPIENT]
        await hub.send_sms(recipient, call.data[ATTR_TEXT])

    async def async_refresh_sms(call: ServiceCall) -> None:
        hub = _get_hub(hass, call.data)
        await hub.fetch_sms_messages()

    async def async_get_sms(call: ServiceCall) -> ServiceResponse:
        hub = _get_hub(hass, call.data)
        await hub.fetch_sms_messages()
        return {
            "messages": [
                {
                    "id": msg.message_id,
                    "phone_number": msg.phone_number,
                    "direction": msg.direction,
                    "status": msg.status_label,
                    "text": msg.text,
                    "timestamp": msg.timestamp,
                }
                for msg in hub.sms_messages.values()
            ]
        }

    async def async_remove_sms(call: ServiceCall) -> None:
        hub = _get_hub(hass, call.data)
        await hub.remove_sms(
            scope=call.data[ATTR_SCOPE],
            message_id=call.data.get(ATTR_MESSAGE_ID),
        )

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
                vol.Required(ATTR_SCOPE, default=10): vol.In([0, 1, 2, 3, 4, 5, 10, 11, 12, 13]),
                vol.Optional(ATTR_MESSAGE_ID): cv.string,
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
