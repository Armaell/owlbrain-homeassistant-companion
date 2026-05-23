from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.restore_state import RestoreEntity
from .entity import OwlBrainEntity

async def async_setup_entry(hass, entry, async_add_entities):
    registry = hass.data["owlbrain"][entry.entry_id]

    entities = []

    for entity in registry.data["entities"].values():
        if entity["platform"] == "sensor":
            entities.append(OwlBrainSensor(registry, entity))

    registry.register_adder("sensor", async_add_entities)

    async_add_entities(entities)


class OwlBrainSensor(OwlBrainEntity, SensorEntity, RestoreEntity):
    @property
    def native_value(self):
        return self._data.get("state")

    @property
    def native_unit_of_measurement(self):
        return self._data.get("unit_of_measurement")

    @property
    def device_class(self):
        return self._data.get("device_class")

    @property
    def state_class(self):
        return self._data.get("state_class")

    @property
    def suggested_display_precision(self):
        return self._data.get("precision")
