from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.restore_state import RestoreEntity
from .entity import OwlBrainEntity


async def async_setup_entry(hass, entry, async_add_entities):
    registry = hass.data["owlbrain"][entry.entry_id]

    entities = []

    for entity in registry.data["entities"].values():
        if entity["platform"] == "button":
            entities.append(OwlBrainButton(registry, entity))

    registry.register_adder("button", async_add_entities)

    async_add_entities(entities)


class OwlBrainButton(OwlBrainEntity, ButtonEntity, RestoreEntity):

    async def async_press(self) -> None:
        await self.registry.update_entity_state(
            self._data["namespace"],
            self._data["id"],
            True,
        )

    @property
    def device_class(self):
        return self._data.get("device_class")
