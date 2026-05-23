from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, SUPPORTED_ENTITY_TYPES
from .storage import OwlBrainStorage
from .registry import OwlBrainRegistry
from .websocket import register_ws

async def async_setup(hass: HomeAssistant, config):
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    storage = OwlBrainStorage(hass)
    registry = OwlBrainRegistry(hass, storage, entry)

    await registry.async_load()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = registry


    register_ws(hass, registry)

    await hass.config_entries.async_forward_entry_setups(
        entry,
        list(SUPPORTED_ENTITY_TYPES)
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    hass.data[DOMAIN].pop(entry.entry_id)
    return True
