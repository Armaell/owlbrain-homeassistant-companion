from homeassistant.components.select import SelectEntity
from homeassistant.helpers.restore_state import RestoreEntity
from .entity import OwlBrainEntity


async def async_setup_entry(hass, entry, async_add_entities):
    registry = hass.data["owlbrain"][entry.entry_id]

    entities = []

    for entity in registry.data["entities"].values():
        if entity["platform"] == "select":
            entities.append(OwlBrainSelect(registry, entity))

    registry.register_adder("select", async_add_entities)

    async_add_entities(entities)


class OwlBrainSelect(OwlBrainEntity, SelectEntity, RestoreEntity):

    @property
    def current_option(self):
        return self._data.get("state")

    @property
    def options(self):
        return self._data.get("options", [])

    async def async_select_option(self, option: str):
        await self.registry.update_entity_state(
            self._data["namespace"],
            self._data["id"],
            option,
        )
