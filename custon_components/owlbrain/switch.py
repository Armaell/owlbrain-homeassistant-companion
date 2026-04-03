from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.restore_state import RestoreEntity
from .entity import OwlBrainEntity

async def async_setup_entry(hass, entry, async_add_entities):
    registry = hass.data["owlbrain"][entry.entry_id]

    entities = []

    for entity in registry.data["entities"].values():
        if entity["platform"] == "switch":
            entities.append(OwlBrainSwitch(registry, entity))

    registry.register_adder("switch", async_add_entities)

    async_add_entities(entities)


class OwlBrainSwitch(OwlBrainEntity, SwitchEntity, RestoreEntity):
    @property
    def is_on(self):
        return bool(self._data.get("state"))

    @property
    def state(self):
        state = self._data.get("state")
        if state is None:
            return None
        return "on" if state else "off"


    async def async_turn_on(self, **kwargs):
        await self.registry.update_entity_state(
            self._data["namespace"],
            self._data["id"],
            True,
        )

    async def async_turn_off(self, **kwargs):
        await self.registry.update_entity_state(
            self._data["namespace"],
            self._data["id"],
            False,
        )
