from homeassistant.helpers.storage import Store
from .const import STORAGE_KEY, STORAGE_VERSION

class OwlBrainStorage:
    def __init__(self, hass):
        self.store = Store(hass, STORAGE_VERSION, STORAGE_KEY)

    async def async_load(self):
        return await self.store.async_load() or {"devices": {}, "entities": {}}

    async def async_save(self, data):
        await self.store.async_save(data)
