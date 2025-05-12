"""Support for remote through the Optoproj API."""
from __future__ import annotations

import logging

from collections.abc import Sequence
from typing import Any


from homeassistant.components.remote import RemoteEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DATA_BROKERS, DOMAIN


_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add remotes for a config entry."""
    
    _LOGGER.debug("Adding remote") 
    
    async_add_entities([OptoProjRemoteEntity(config_entry)])

    
class OptoProjRemoteEntity(RemoteEntity):
    
#    _attr_supported_features = RemoteEntityFeature.ACTIVITY

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize the entity."""
        
        _LOGGER.debug("Initialize the OptoProjRemoteEntity entity.")
        super().__init__()        
            
        entry_data = config_entry.runtime_data    
        self._api = entry_data.api
        self._device_id = entry_data.device_data["id"]
            
        self._name = "Remote"
        self._attr_name = self._device_id+" Remote"        
        self._attr_unique_id = self._device_id+"_remote"

        device_info = entry_data.device_data

        self._attr_device_info = DeviceInfo(
            identifiers={(self._device_id, self._attr_unique_id)},
            name="Projector",
            manufacturer="Optoma",
            model=device_info["device_model"],
        )
        
        _LOGGER.debug("Initialize the OptoProjRemoteEntity entity done. self._name:%s self._attr_unique_id:%s device_id:%s self._attr_device_info:%s", self._name, self._attr_unique_id, self._device_id, self._attr_device_info )        

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the projector on."""
        _LOGGER.debug("Send Turn On Command") 

        await self._api.async_send_turn_on(self._device_id)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the projector off."""
        _LOGGER.debug("Send Turn Off Command") 
                
        await self._api.async_send_turn_off(self._device_id)

           
    
