from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_ID,
    CONF_MAC,
    CONF_PASSWORD,
    CONF_UNIQUE_ID,
    CONF_USERNAME,
)
from homeassistant.core import HomeAssistant

from .hub import GLinetHub

TO_REDACT = {
    CONF_HOST,
    CONF_MAC,
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_UNIQUE_ID,
    CONF_ID,
    "ssid",
    "bssid",
    "key",
    "ip",
    "gateway",
    "dns",
    "address",
    "mac",
    "imei",
    "iccid",
    "phone_number",
    "body",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    hub: GLinetHub = entry.runtime_data

    diag_data = {
        "entry": async_redact_data(entry.as_dict(), TO_REDACT),
        "hub_state": {
            "hub_name": hub.hub_name,
            "device_mac": hub.device_mac,
            "device_model": hub.device_model,
            "firmware_version": hub.firmware_version,
            "uptime": hub.router_status.uptime if hub.router_status else None,
            "load_average": hub.router_status.load_average if hub.router_status else None,
            "memory": (
                {
                    "total": hub.router_status.memory_total,
                    "used": hub.router_status.memory_used,
                    "free": hub.router_status.memory_free,
                }
                if hub.router_status
                else None
            ),
            "wifi_interfaces": [
                {
                    "name": name,
                    "enabled": iface.enabled,
                    "guest": iface.guest,
                    "hidden": iface.hidden,
                    "encryption": iface.encryption,
                }
                for name, iface in hub.wifi_interfaces.items()
            ],
            "repeater": {
                "connected": hub.repeater_connected,
                "status": (
                    {
                        "state": hub.repeater_status.state.name,
                        "fail_type": hub.repeater_status.fail_type,
                    }
                    if hub.repeater_status
                    else None
                ),
            },
            "cellular": {
                "modems": [
                    {
                        "bus": modem.get("bus"),
                        "model": modem.get("model"),
                        "status": modem.get("status"),
                        "signal": modem.get("signal"),
                        "network_type": modem.get("network_type"),
                    }
                    for modem in hub.cellular_status.get("modems", [])
                ],
                "default_bus": hub.default_modem_bus,
            },
            "vpn": {
                "active_connections": [
                    {"name": conn.name, "connected": conn.connected}
                    for conn in hub.active_vpn_connections or []
                ],
            },
            "tailscale": {
                "connected": hub.tailscale_connected,
            },
            "features": list(hub.enabled_features),
        },
    }

    return async_redact_data(diag_data, TO_REDACT)
