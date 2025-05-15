"""Config flow for Optoproj integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .const import DOMAIN, NAME
from .optoapi import OptoApi
from .exceptions import CannotConnect, InvalidAuth

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)

async def _validate_login(
    hass: HomeAssistant, login_data: dict[str, Any]
) -> tuple[dict[str, str], list[dict[str, Any]] | None]:
    """Validate login data and return any errors and device list."""
    api = OptoApi(
        async_create_clientsession(hass),
        login_data[CONF_USERNAME],
        login_data[CONF_PASSWORD],
    )
    errors: dict[str, str] = {}
    device_list = None
    try:
        await api.async_login()
        device_list = await api.async_get_device_list()
        _LOGGER.debug("Fetched device list during config flow: %s", device_list)
    except InvalidAuth:
        _LOGGER.exception("Login failed for %s", login_data[CONF_USERNAME])
        errors["base"] = "login_failed"
    except CannotConnect:
        _LOGGER.exception("Could not connect to %s", login_data[CONF_USERNAME])
        errors["base"] = "cannot_connect"
    return errors, device_list

class OptoprojConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Optoproj."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        device_list = None

        if user_input is not None:
            # Set unique ID based on username to prevent duplicate entries
            unique_id = user_input[CONF_USERNAME]
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()

            errors, device_list = await _validate_login(self.hass, user_input)
            if not errors:
                # Store device list in config entry data
                return self.async_create_entry(
                    title=NAME,
                    data={
                        CONF_USERNAME: user_input[CONF_USERNAME],
                        CONF_PASSWORD: user_input[CONF_PASSWORD],
                        "devices": device_list,
                    },
                )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )