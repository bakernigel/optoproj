"""Implementation of Optoma JSON API."""

import dataclasses
from datetime import date, datetime
from enum import Enum
import json
import logging
from typing import Any, Optional, Union
from urllib.parse import urlencode

import aiohttp
from aiohttp.client_exceptions import ClientResponseError
import aiozoneinfo
import arrow


from .exceptions import CannotConnect, InvalidAuth


_LOGGER = logging.getLogger(__file__)

class OptoApi:

    def __init__(
        self,
        session: aiohttp.ClientSession,
        username: str,
        password: str,
    ) -> None:
        """Initialize."""
        self.session: aiohttp.ClientSession = session
        self.username: str = username
        self.password: str = password
        self.access_token: Optional[str] = None
        _LOGGER.debug("OptoApi init username:%s password:%s",username,password)


    async def async_login(self) -> None:
        """Login to the utility website."""
        _LOGGER.debug("Starting login process for Optoma username:%s password:%s",self.username,self.password)

        session = self.session
        payload = {"login_name":self.username,"password":self.password}    

        headers = {
            "accept": "*/*",
            "content-type": "application/json"
        }
 
        # Send the POST request
        async with session.post(
            "https://omw.optoma.com/member/login",
            json=payload,
            headers=headers,
            raise_for_status=True,
        ) as resp:
            login_result = await resp.json(content_type=None)
            if login_result["result_code"] != 200:
               raise InvalidAuth("Username and password failed")

        _LOGGER.debug("Optoma Login result: %s",login_result)
        
        self.access_token = login_result["result"]["token"]
        
    async def async_get_device_list(self):  
        _LOGGER.debug("async_get_device_list")
        session = self.session    
    
        url = "https://omw.optoma.com/device"

        headers = {
          "accept": "application/json, text/plain, */*",
          "authorization": "Bearer "+self.access_token,
        }

        async with session.get(url, data=None, headers=headers) as resp:
            login_result = await resp.json(content_type=None)
            
        _LOGGER.debug("async_get_device_list login_result:%s",login_result)
        
# Uncomment below to test the 2 device case 
#        device_list_test= login_result["result"]
#        _LOGGER.debug("Actual device list:%s",device_list_test) 
#        test_device_list = []
#        device0 = device_list_test[0]
#        _LOGGER.debug("Device0:%s",device0) 
#        test_device_list.append(device0)
#        device1 = {'id': '12345', 'sn_num': 'Q7JL226KAAAAB0595', 'alexa_alias': 'my_room', 'device_model': 'UHZ99'}
#        _LOGGER.debug("Device1:%s",device1) 
#        test_device_list.append(device1)                    
#        _LOGGER.debug("Modified test_device_list:%s",test_device_list)    
#        device_list = test_device_list
        
        
        device_list = login_result["result"]
        return device_list    
        
    async def async_send_turn_on(self, device_id) -> None:  
        _LOGGER.debug("async_send_turn_on")
        session = self.session    
    
        url = "https://omw.optoma.com/device/run_task"

        headers = {
          "accept": "*/*",
          "content-type": "application/json",
          "authorization": "Bearer "+self.access_token,
        }
        payload = {
            "com_value" : "1", #on
            "job_type" : "1",
            "device_id" : device_id,
            "com_id" : "1"
        }    
        
        async with session.post(url, json=payload, headers=headers) as resp:
            result = await resp.json(content_type=None)
        _LOGGER.debug("async_send_turn_on result:%s", result)       
            
    async def async_send_turn_off(self, device_id) -> None:  
        _LOGGER.debug("async_send_turn_off")
        session = self.session    
    
        url = "https://omw.optoma.com/device/run_task"

        headers = {
          "accept": "*/*",
          "content-type": "application/json",
          "authorization": "Bearer "+self.access_token,
        }
        payload = {
            "com_value" : "2", #off
            "job_type" : "1",
            "device_id" : device_id,
            "com_id" : "1"
        }    
        
        async with session.post(url, json=payload, headers=headers) as resp:
            result = await resp.json(content_type=None)
        _LOGGER.debug("async_send_turn_off result:%s", result)    
            


    def _get_headers(self, customer_uuid: Optional[str] = None) -> dict[str, str]:
        headers = {"User-Agent": "Optoma%20InfoWall/48 CFNetwork/3826.500.111.2.2 Darwin/24.4.0"}
        if self.access_token:
            headers["authorization"] = f"Bearer {self.access_token}"

        return headers


