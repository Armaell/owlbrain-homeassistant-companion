from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .manager import OwlBrainManager


async def async_setup_entry(
	hass: HomeAssistant,
	entry: ConfigEntry,
	async_add_entities: AddEntitiesCallback,
) -> None:
	manager: OwlBrainManager = hass.data[DOMAIN]["manager"]
	platform = entity_platform.async_get_current_platform()
	manager.entities.register_platform("button", platform.async_add_entities)
