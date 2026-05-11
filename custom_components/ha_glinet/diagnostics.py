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
    "apn",
    "network_id",
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
            "router_model": hub.router_model,
            "firmware_version": hub.firmware_version,
            "uptime": hub.router_status.uptime if hub.router_status else None,
            "cpu_temperature": hub.router_status.temperature if hub.router_status else None,
            "load_average": hub.router_status.load_average if hub.router_status else None,
            "memory": (
                {
                    "total": hub.router_status.memory_total,
                    "used": hub.router_status.memory_total - hub.router_status.memory_free,
                    "free": hub.router_status.memory_free,
                }
                if hub.router_status
                else None
            ),
            "flash": (
                {
                    "total": hub.router_status.flash_total,
                    "free": hub.router_status.flash_free,
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
                        "apn": modem.get("apn") or modem.get("simcard", {}).get("apn"),
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
            "zerotier": {
                "connected": hub.zerotier_status.connected if hub.zerotier_status else None,
                "network_id": hub.zerotier_status.network_id if hub.zerotier_status else None,
            },
            "adguard": {
                "enabled": hub.adguard_status.enabled if hub.adguard_status else None,
                "dns_enabled": hub.adguard_status.dns_enabled if hub.adguard_status else None,
            },
            "led_enabled": hub.led_enabled,
            "fan": {
                "speed": hub.fan_speed,
                "running": hub.fan_running,
                "threshold": hub.fan_temperature_threshold,
            },
            "wg_server": {
                "users_count": hub.wg_server_connected_users,
            },
            "ovpn_server": {
                "users_count": hub.ovpn_server_connected_users,
            },
            "sms": {
                "message_count": len(hub.sms_messages),
            },
            "tracked_devices": [
                {
                    "mac": mac,
                    "name": device.name,
                    "ip": device.ip_address,
                    "connected": device.is_connected,
                    "interface": device.interface_type.name,
                }
                for mac, device in hub.tracked_devices.items()
            ],
            "features": list(hub.enabled_features),
        },
    }

    return async_redact_data(diag_data, TO_REDACT)
