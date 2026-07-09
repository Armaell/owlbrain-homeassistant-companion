from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity

from ..const import DOMAIN
from ..models.entity import EntityModel


class OwlBrainBaseEntity(Entity):
	"""Base class to all entity domains."""

	_attr_should_poll = False

	def __init__(
		self, hass: HomeAssistant, manager, model: EntityModel
	) -> None:
		self.hass = hass
		self._manager = manager
		self._model = model

		self.entity_id = model.entity_id

		self._attr_unique_id = model.unique_id
		self._attr_name = model.metadata.get("name")

		self._attr_has_entity_name = False

	@property
	def available(self) -> bool:
		"""Availability can be controlled by data.available.

		It also requires an active and subscribed connection.
		"""
		return self._model.data.get(
			"available"
		) is not False and self._manager.broadcaster.available(
			self.owl_namespace
		)

	@property
	def name(self) -> str | None:
		return self._model.metadata.get("name")

	@property
	def device_info(self) -> dict[str, Any] | None:
		"""Return device info if this entity is attached to a device."""
		device_id = self._model.metadata.get("device_id")

		if not device_id:
			return None

		device = self._manager.store.sync_get_device(
			self.owl_namespace, device_id
		)
		if not device:
			return None

		metadata = device.metadata
		return {
			"identifiers": {(DOMAIN, device.unique_id)},
			"connections": metadata.get("connections"),
			"manufacturer": metadata.get("manufacturer"),
			"model": metadata.get("model"),
			"name": metadata.get("name"),
			"sw_version": metadata.get("sw_version"),
			"hw_version": metadata.get("hw_version"),
			"serial_number": metadata.get("serial_number"),
			"via_device": metadata.get("via_device"),
			"suggested_area": metadata.get("suggested_area"),
			"configuration_url": metadata.get("configuration_url"),
		}

	@property
	def entity_category(self) -> str | None:
		return self._model.metadata.get("entity_category")

	@property
	def icon(self) -> str | None:
		return self._model.metadata.get("icon")

	@property
	def translation_key(self) -> str | None:
		return self._model.metadata.get("translation_key")

	@property
	def entity_picture(self) -> str | None:
		return self._model.metadata.get("entity_picture")

	@classmethod
	def validate_metadata(cls, metadata: dict[str, Any]) -> dict[str, Any]:
		"""Validate and normalize metadata."""
		return dict(metadata)

	@classmethod
	def validate_data(
		cls,
		metadata: dict[str, Any],
		current_data: dict[str, Any],
		new_data: dict[str, Any],
	) -> dict[str, Any]:
		"""Validate incoming data and merge it onto `current_data`."""
		updated = dict(current_data)

		if "available" in new_data:
			updated["available"] = bool(new_data["available"])

		return updated

	async def async_update_metadata(
		self, metadata: dict[str, Any]
	) -> dict[str, Any]:
		normalized = self.validate_metadata(metadata)
		self._model.metadata = normalized
		self.async_write_ha_state()
		return normalized

	async def async_update_data(
		self, new_data: dict[str, Any]
	) -> dict[str, Any]:
		updated = self.validate_data(
			self.owl_model.metadata, self.owl_model.data, new_data
		)
		self.owl_model.data = updated
		self.async_write_ha_state()
		return updated

	@property
	def owl_model(self) -> EntityModel:
		"""Expose the underlying model to subclasses."""
		return self._model

	@property
	def owl_namespace(self) -> str:
		return self._model.namespace

	@property
	def owl_entity_id(self) -> str:
		return self._model.entity_id

	async def _broadcast_entity_action(self, action: str, data: Any):
		await self._manager.broadcaster.broadcast_entity_action(
			self.owl_namespace, self.owl_entity_id, action, data
		)
