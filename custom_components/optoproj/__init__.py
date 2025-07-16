"""The Optoproj integration."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN
from .optoapi import OptoApi

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.REMOTE, Platform.SELECT]

@dataclass
class OptoProjData:
    """Define an object to hold OptoProjData data."""
    device_data: dict[str, Any]
    device_id: str
    api: OptoApi

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Optoproj from a config entry."""
    _LOGGER.debug("Setting up Optoproj config entry: %s", entry.entry_id)
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault(entry.entry_id, {"devices": {}})

    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]

    api = OptoApi(
        async_create_clientsession(hass),
        username,
        password,
    )

    try:
        await api.async_login()
        _LOGGER.debug("Login successful, token: %s", api.access_token)

        device_list = await api.async_get_device_list()
        _LOGGER.debug("Device list: %s", device_list)

        device_registry = dr.async_get(hass)
        devices = {}
        for device in device_list:
            device_id = device["id"]
            _LOGGER.debug("Processing device: %s", device_id)

            # Store device data
            devices[device_id] = OptoProjData(
                device_data=device,
                device_id=device_id,
                api=api,
            )
# Below doesn't seem to be needed. Device info gets added in remote.py
            # Register device in Device Registry
#            device_registry.async_get_or_create(
#                config_entry_id=entry.entry_id,
#                identifiers={(DOMAIN, device_id)},
#                manufacturer="Optoma",
#                name=device.get("name", device_id),
#                model=device["device_model"],
#                configuration_url="https://omw.optoma.com",
#            )

        # Store all devices in hass.data
        hass.data[DOMAIN][entry.entry_id]["devices"] = devices

        # Set up the remote platform once
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        return True

    except Exception as err:
        _LOGGER.error("Failed to set up Optoproj: %s", err)
        raise

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok