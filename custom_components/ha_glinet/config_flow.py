from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components.device_tracker import CONF_CONSIDER_HOME, DEFAULT_CONSIDER_HOME
from homeassistant.const import CONF_HOST, CONF_MAC, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import AbortFlow
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import format_mac

from .api import GLinetApiClient, NonZeroResponse
from .const import (
    API_PATH,
    CONF_ENABLED_FEATURES,
    CONF_TITLE,
    DEFAULT_PASSWORD,
    DEFAULT_URL,
    DEFAULT_USERNAME,
    DOMAIN,
    FEATURE_CELLULAR,
    FEATURE_REPEATER,
    FEATURE_SMS,
    FEATURE_TAILSCALE,
    FEATURE_WIREGUARD,
    INTEGRATION_NAME,
)
from .utils import compute_mac_offset

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigFlowResult
    from homeassistant.helpers.service_info.dhcp import DhcpServiceInfo

_LOGGER = logging.getLogger(__name__)

FEATURE_OPTIONS = [
    {"label": "Cellular", "value": FEATURE_CELLULAR},
    {"label": "Repeater", "value": FEATURE_REPEATER},
    {"label": "SMS", "value": FEATURE_SMS},
    {"label": "Tailscale", "value": FEATURE_TAILSCALE},
    {"label": "WireGuard", "value": FEATURE_WIREGUARD},
]
DEFAULT_ENABLED_FEATURES = [
    FEATURE_CELLULAR,
    FEATURE_REPEATER,
    FEATURE_SMS,
    FEATURE_TAILSCALE,
    FEATURE_WIREGUARD,
]

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, default=DEFAULT_URL): selector.TextSelector(
            selector.TextSelectorConfig(type=selector.TextSelectorType.URL)
        ),
        vol.Required(CONF_PASSWORD, default=DEFAULT_PASSWORD): selector.TextSelector(
            selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
        ),
        vol.Optional(
            CONF_CONSIDER_HOME,
            default=DEFAULT_CONSIDER_HOME.total_seconds(),
        ): vol.All(vol.Coerce(int), vol.Clamp(min=0, max=900)),
        vol.Optional(
            CONF_ENABLED_FEATURES,
            default=DEFAULT_ENABLED_FEATURES,
        ): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=FEATURE_OPTIONS,
                multiple=True,
            )
        ),
    }
)


class SetupHub:

    def __init__(self, host: str, hass: HomeAssistant) -> None:
        self.host = host
        self.username = DEFAULT_USERNAME
        self.router = GLinetApiClient(
            base_url=f"{host}{API_PATH}",
            session=async_get_clientsession(hass),
        )
        self.router_mac = ""
        self.router_model = ""

    async def check_reachable(self) -> bool:
        try:
            return await self.router.is_router_reachable(self.username)
        except (ConnectionError, TypeError):
            _LOGGER.exception("Failed to connect to %s", self.host)
            return False

    async def attempt_login(self, password: str) -> bool:
        try:
            await self.router.authenticate(self.username, password)
            info = await self.router.system.get_info()
        except (ConnectionRefusedError, NonZeroResponse):
            _LOGGER.info("Failed to authenticate with GL-INet router during validation")
            return False

        self.router_mac = str(info[CONF_MAC])
        self.router_model = str(info["model"])
        return self.router.logged_in


async def process_user_input(
    data: dict[str, Any], hass: HomeAssistant, raise_on_invalid_auth: bool = True
) -> dict[str, Any]:
    hub = SetupHub(data[CONF_HOST], hass)
    if not await hub.check_reachable():
        raise CannotConnect

    valid_auth = await hub.attempt_login(data.get(CONF_PASSWORD, DEFAULT_PASSWORD))
    if raise_on_invalid_auth and not valid_auth:
        raise InvalidAuth

    return {
        CONF_TITLE: f"{INTEGRATION_NAME} {hub.router_model.upper()}",
        CONF_MAC: hub.router_mac,
        "data": {
            CONF_USERNAME: DEFAULT_USERNAME,
            CONF_HOST: data[CONF_HOST],
            CONF_PASSWORD: data.get(CONF_PASSWORD, DEFAULT_PASSWORD) if valid_auth else "",
            CONF_CONSIDER_HOME: data.get(
                CONF_CONSIDER_HOME,
                DEFAULT_CONSIDER_HOME.total_seconds(),
            ),
            CONF_ENABLED_FEATURES: data.get(
                CONF_ENABLED_FEATURES,
                DEFAULT_ENABLED_FEATURES,
            ),
        },
    }


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1

    def __init__(self) -> None:
        self._discovered_data: dict[str, Any] | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await process_user_input(user_input, self.hass)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                unique_id = format_mac(info[CONF_MAC])
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=info[CONF_TITLE], data=info["data"])

        defaults = user_input or self._discovered_data or {}
        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(STEP_USER_DATA_SCHEMA, defaults),
            errors=errors,
        )

    async def async_step_dhcp(self, discovery_info: DhcpServiceInfo) -> ConfigFlowResult:
        discovery_input = {CONF_HOST: f"http://{discovery_info.ip}"}
        self._async_abort_entries_match(discovery_input)

        unique_id = compute_mac_offset(discovery_info.macaddress, -1).lower()
        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()

        if {unique_id, format_mac(discovery_info.macaddress)}.intersection(
            self._async_current_ids(include_ignore=True)
        ):
            raise AbortFlow("already_configured")

        try:
            entry = await process_user_input(
                discovery_input,
                hass=self.hass,
                raise_on_invalid_auth=False,
            )
        except CannotConnect:
            return self.async_abort(reason="cannot_connect")

        self._discovered_data = entry["data"]
        return await self.async_step_user()

    @staticmethod
    @callback
    def async_get_options_flow(_: config_entries.ConfigEntry) -> OptionsFlowHandler:
        return OptionsFlowHandler()


class OptionsFlowHandler(config_entries.OptionsFlow):

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await process_user_input(user_input, self.hass)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title="",
                    data=self.config_entry.options | info["data"],
                )

        data_schema = self.add_suggested_values_to_schema(
            STEP_USER_DATA_SCHEMA,
            {**self.config_entry.data, **self.config_entry.options},
        )
        return self.async_show_form(step_id="init", data_schema=data_schema, errors=errors)


class CannotConnect(HomeAssistantError):
    pass


class InvalidAuth(HomeAssistantError):
    pass
