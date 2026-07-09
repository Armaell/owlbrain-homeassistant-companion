from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
	SensorDeviceClass,
	SensorEntity,
	SensorStateClass,
)

from ..utils.validation import ensure_in_enum, ensure_str
from .base import OwlBrainBaseEntity


class OwlBrainSensorEntity(OwlBrainBaseEntity, SensorEntity):
	@property
	def native_value(self) -> Any:
		return self.owl_model.data.get("state")

	@property
	def native_unit_of_measurement(self) -> str | None:
		return self.owl_model.metadata.get("unit")

	@property
	def device_class(self) -> str | None:
		return self.owl_model.metadata.get("device_class")

	@property
	def state_class(self) -> str | None:
		return self.owl_model.metadata.get("state_class")

	@classmethod
	def validate_metadata(cls, metadata: dict) -> dict:
		"""Validate and normalize metadata.

		Accepted keys:
		- unit: str
		- device_class: str
		- state_class: str
		- any other base keys
		"""
		normalized = super().validate_metadata(metadata)

		if "unit" in normalized:
			normalized["unit"] = ensure_str("unit", normalized["unit"])

		if "device_class" in normalized:
			normalized["device_class"] = ensure_in_enum(
				"device_class", normalized["device_class"], SensorDeviceClass
			)

		if "state_class" in normalized:
			normalized["state_class"] = ensure_in_enum(
				"state_class", normalized["state_class"], SensorStateClass
			)

		return normalized

	@classmethod
	def validate_data(
		cls,
		metadata: dict[str, Any],
		current_data: dict[str, Any],
		new_data: dict[str, Any],
	) -> dict[str, Any]:
		"""Validate and merge incoming data.

		Accepted keys:
		- state: any
		- available: bool
		"""
		updated = dict(current_data)

		if "state" in new_data:
			updated["state"] = new_data["state"]

		return super().validate_data(metadata, updated, new_data)
