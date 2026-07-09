from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, PLATFORMS
from .manager import OwlBrainManager
from .store import OwlBrainStore
from .websocket_api import async_register_websocket_api

_LOGGER = logging.getLogger(__name__)

DOMAIN = DOMAIN


async def async_setup(hass: HomeAssistant, config: ConfigType):
	return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
	store = OwlBrainStore(hass)
	manager = OwlBrainManager(hass, store)

	hass.data.setdefault(DOMAIN, {})["manager"] = manager

	await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

	await manager.entities.restore_runtime_entities()

	async_register_websocket_api(hass, manager)

	_LOGGER.info("OwlBrain integration initialized")
	return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
	unload_ok = await hass.config_entries.async_unload_platforms(
		entry, PLATFORMS
	)

	if unload_ok:
		hass.data[DOMAIN].pop("manager", None)

	return unload_ok
