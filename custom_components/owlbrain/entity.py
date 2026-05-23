from homeassistant.helpers.entity import Entity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.restore_state import RestoreEntity
from .const import DOMAIN

class OwlBrainEntity(Entity):
    def __init__(self, registry, data):
        self.registry = registry
        self._data = data
        self._attr_unique_id = data["unique_id"]
        self._attr_name = data.get("name", data["id"])
        self._attr_has_entity_name = True

    @property
    def entity_registry_enabled_default(self):
        return True

    @property
    def should_poll(self):
        return False

    @property
    def extra_state_attributes(self):
        return self._data.get("attributes")

    @property
    def available(self):
        return True

    @property
    def native_value(self):
        return self._data.get("state")

    @property
    def device_info(self):
        if not self._data.get("device_id"):
            return None

        namespace = self._data["namespace"]
        device_id = self._data["device_id"]

        return DeviceInfo(
            identifiers={(DOMAIN, f"{namespace}:{device_id}")},
        )

    async def async_added_to_hass(self):
        await super().async_added_to_hass()

        if self._data.get("state") is not None:
            return

        # Otherwise fallback to HA restore
        last_state = await self.async_get_last_state()
        if last_state is not None:
            self._data["state"] = last_state.state
            self._data["attributes"] = last_state.attributes

    def update_from_registry(self, data):
        self._data = data
        self._attr_name = data.get("name", data["id"])
        self.async_write_ha_state()

    @property
    def icon(self):
        return self._data.get("icon")

    @property
    def entity_category(self):
        return self._data.get("entity_category")
