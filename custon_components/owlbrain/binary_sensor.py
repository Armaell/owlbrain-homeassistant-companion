from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.restore_state import RestoreEntity
from .entity import OwlBrainEntity

async def async_setup_entry(hass, entry, async_add_entities):
    registry = hass.data["owlbrain"][entry.entry_id]

    entities = []

    for entity in registry.data["entities"].values():
        if entity["platform"] == "binary_sensor":
            entities.append(OwlBrainBinarySensor(registry, entity))

    registry.register_adder("binary_sensor", async_add_entities)

    async_add_entities(entities)


class OwlBrainBinarySensor(OwlBrainEntity, BinarySensorEntity, RestoreEntity):
    @property
    def is_on(self):
        return bool(self._data.get("state"))

    @property
    def device_class(self):
        return self._data.get("device_class")
