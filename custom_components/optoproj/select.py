"""Support for select through the Optoproj API."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.select import SelectEntity
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
    """Add select for a config entry."""
    _LOGGER.debug("Setting up select platform for entry: %s", config_entry.entry_id)
    
    devices = hass.data[DOMAIN][config_entry.entry_id]["devices"]
    entities = [
        OptoProjSelectEntity(device_data, config_entry)
        for device_data in devices.values()
    ]
    _LOGGER.debug("Adding %d select entities", len(entities))
    async_add_entities(entities)

class OptoProjSelectEntity(SelectEntity):
    """Representation of an Optoma Projector select entity."""

    def __init__(self, device_data: OptoProjData, config_entry: ConfigEntry) -> None:
        """Initialize the entity."""
        self._device_data = device_data
        self._api = device_data.api
        self._device_id = device_data.device_id
        self._attr_unique_id = f"{self._device_id}_input_select"
        self._attr_name = device_data.device_data.get("name", f"{self._device_id} Input Select")

        _LOGGER.debug(
            "Initialized OptoProjSelectEntity: name=%s, unique_id=%s, device_id=%s",
            self._attr_name, self._attr_unique_id, self._device_id
        )

    _attr_options = [
        "HDMI1",
        "HDMI2",
        "HDMI3"
    ]
    
    _attr_current_option = None

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
        
    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        _LOGGER.debug("Changing the selected option to: %s", option)
        
        # Send the command to the device via the API
        await self._api.async_send_input_select(self._device_id, option)
        
        # Update the current option
        self._attr_current_option = option
        
        # Notify Home Assistant of the state change
        self.async_write_ha_state()