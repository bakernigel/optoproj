"""Support for remote through the Optoproj API."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.remote import RemoteEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN
from . import OptoProjData

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add remotes for a config entry."""
    _LOGGER.debug("Setting up remote platform for entry: %s", config_entry.entry_id)
    
    devices = hass.data[DOMAIN][config_entry.entry_id]["devices"]
    entities = [
        OptoProjRemoteEntity(device_data, config_entry)
        for device_data in devices.values()
    ]
    _LOGGER.debug("Adding %d remote entities", len(entities))
    async_add_entities(entities)

class OptoProjRemoteEntity(RemoteEntity):
    """Representation of an Optoma Projector remote entity."""

    def __init__(self, device_data: OptoProjData, config_entry: ConfigEntry) -> None:
        """Initialize the entity."""
        self._device_data = device_data
        self._api = device_data.api
        self._device_id = device_data.device_id
        self._attr_unique_id = f"{self._device_id}_remote"
        self._attr_name = device_data.device_data.get("name", f"{self._device_id} Remote")

        _LOGGER.debug(
            "Initialized OptoProjRemoteEntity: name=%s, unique_id=%s, device_id=%s",
            self._attr_name, self._attr_unique_id, self._device_id
        )

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information for the Device Registry."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name="Projector "+self._device_id,
            manufacturer="Optoma",
            model=self._device_data.device_data.get("device_model", "Optoma Projector"),
            configuration_url="https://omw.optoma.com",
        )

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the projector on."""
        _LOGGER.debug("Sending turn-on command to device: %s", self._device_id)
        await self._api.async_send_turn_on(self._device_id)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the projector off."""
        _LOGGER.debug("Sending turn-off command to device: %s", self._device_id)
        await self._api.async_send_turn_off(self._device_id)