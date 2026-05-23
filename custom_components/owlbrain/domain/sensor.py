from __future__ import annotations

from typing import Any, Dict, Optional

from homeassistant.components.sensor import (
	SensorEntity,
	SensorDeviceClass,
	SensorStateClass
)

from .base import OwlBrainBaseEntity
from ..utils.validation import ensure_str, ensure_in_enum


class OwlBrainSensorEntity(OwlBrainBaseEntity, SensorEntity):

	@property
	def native_value(self) -> Any:
		return self.owl_model.data.get("value")

	@property
	def native_unit_of_measurement(self) -> Optional[str]:
		return self.owl_model.metadata.get("unit")

	@property
	def device_class(self) -> Optional[str]:
		return self.owl_model.metadata.get("device_class")

	@property
	def state_class(self) -> Optional[str]:
		return self.owl_model.metadata.get("state_class")

	async def async_update_metadata(self, metadata: dict) -> None:
		"""Validate and overwrite metadata into the entity model.

		Accepted keys:
		- unit: str
		- device_class: str
		- state_class: str
		- any other base keys
		"""
		if "unit" in metadata:
			u = ensure_str("unit", metadata["unit"])
			metadata["unit"] = u

		if "device_class" in metadata:
			dc = ensure_in_enum("device_class", metadata["device_class"], SensorDeviceClass)
			metadata["device_class"] = dc

		if "state_class" in metadata:
			sc = ensure_in_enum("state_class", metadata["state_class"], SensorStateClass)
			metadata["state_class"] = sc

		return await super().async_update_metadata(metadata)


	async def async_update_data(self, new_data: Dict[str, Any]) -> Dict[str, Any]:
		"""Validate and merge incoming data into the entity model.

		Accepted keys:
		- value: any
		- available: bool
		"""
		updated = dict(self.owl_model.data)

		if "value" in new_data:
			updated["value"] = new_data["value"]

		self.owl_model.data = updated
		return await super().async_update_data(new_data)
