"""The Optoproj integration."""

from __future__ import annotations

import logging

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.const import (
    CONF_DEVICES,
    CONF_PARAMS,
)

from .const import DOMAIN
from .optoapi import OptoApi

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.REMOTE]

@dataclass
class OptoProjData:
    """Define an object to hold OptoProjData data."""
    device_data: dict[str, str]
    device_id: str
    api: OptoApi


OptoProjConfigEntry = ConfigEntry[OptoProjData]


async def async_setup_entry(hass: HomeAssistant, entry: OptoProjConfigEntry) -> bool:
    """Set up Optoproj from a config entry."""
    _LOGGER.debug("Set up Optoproj from a config entry: %s", entry.data)
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault(entry.entry_id, {})
    entry_data = hass.data[DOMAIN][entry.entry_id]
    entry_data[CONF_PARAMS] = entry.data
    
    username = entry.data["username"]
    password = entry.data["password"]
    
    api = OptoApi(
        async_create_clientsession(hass),
        username,
        password,
    )
    
    await api.async_login()
    
    token = api.access_token
    
    _LOGGER.debug("async_setup_entry token: %s", token)
    
    device_list = await api.async_get_device_list()
    
#    entry_data[CONF_DEVICES] = device_id

    for device in device_list:
        _LOGGER.debug("async_setup_entry device: %s", device)
        device_id = device["id"]
        conf_data = OptoProjData(device, device_id, api)
        entry.runtime_data = conf_data
        
        _LOGGER.debug("async_setup_entry device_id: %s", device_id)
        
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
