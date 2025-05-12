"""Config flow for Optoproj integration."""

from __future__ import annotations

from collections.abc import Mapping
import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_NAME, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.typing import VolDictType

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
    hass: HomeAssistant, login_data: dict[str, str]
) -> dict[str, str]:
    """Validate login data and return any errors."""
    api = OptoApi(
        async_create_clientsession(hass),
        login_data[CONF_USERNAME],
        login_data[CONF_PASSWORD],
    )
    errors: dict[str, str] = {}
    try:
        await api.async_login()
    except InvalidAuth:
        _LOGGER.exception(
            "Login failed for %s when connecting to Optoma", login_data[CONF_USERNAME]
        )
        errors["base"] = "login_failed"
    except CannotConnect:
        _LOGGER.exception("Could not connect to %s", login_data[CONF_USERNAME])
        errors["base"] = "cannot_connect"
    return errors


class OptoprojConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Optoproj."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize a new OptoprojConfigFlow."""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            self._async_abort_entries_match(
                {
                    CONF_USERNAME: user_input[CONF_USERNAME],
                }
            )

            errors = await _validate_login(self.hass, user_input)
            if not errors:
                return self._async_create_optoproj_entry(user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    @callback
    def _async_create_optoproj_entry(self, data: dict[str, Any]) -> ConfigFlowResult:
        """Create the config entry."""
        return self.async_create_entry(
            title=NAME,
            data=data,
        )