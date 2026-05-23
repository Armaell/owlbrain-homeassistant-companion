from __future__ import annotations

from typing import Any, Dict, Optional

from homeassistant.components.number import (
	NumberEntity,
	NumberMode,
)

from .base import OwlBrainBaseEntity
from ..utils.validation import ensure_float, ensure_str, ensure_in_range, ensure_in_enum

class OwlBrainNumberEntity(OwlBrainBaseEntity, NumberEntity):

	@property
	def native_value(self) -> float:
		return float(self.owl_model.data.get("state", self.native_min_value))

	@property
	def native_min_value(self) -> float:
		return float(self.owl_model.metadata.get("min", 0))

	@property
	def native_max_value(self) -> float:
		return float(self.owl_model.metadata.get("max", 100))

	@property
	def native_step(self) -> float:
		return float(self.owl_model.metadata.get("step", 1))

	@property
	def mode(self) -> NumberMode:
		mode = self.owl_model.metadata.get("mode", "auto")
		return NumberMode(mode)

	@property
	def unit_of_measurement(self) -> Optional[str]:
		return self.owl_model.metadata.get("unit")

	@property
	def device_class(self) -> Optional[str]:
		return self.owl_model.metadata.get("device_class")

	async def async_set_native_value(self, value: float) -> None:
		await self._broadcast_entity_action("set_state", { "state": value })

	async def async_update_metadata(self, metadata: dict) -> None:
		"""Validate and overwrite metadata into the entity model.

		Accepted keys:
		- min: float
		- max: float
		- step: float
		- mode: "auto" | "box" | "slider"
		- unit: str
		- device_class: str
		- any other base keys
		"""

		if "min" in metadata:
			metadata["min"] = ensure_float("min", metadata["min"])

		if "max" in metadata:
			metadata["max"] = ensure_float("max", metadata["max"])

		if "step" in metadata:
			metadata["step"] = ensure_float("step", metadata["step"])

		if "mode" in metadata:
			mode = ensure_str("mode", metadata["mode"])
			ensure_in_enum("mode", mode, NumberMode)
			metadata["mode"] = mode

		if "unit" in metadata:
			metadata["unit"] = ensure_str("unit", metadata["unit"])

		if "device_class" in metadata:
			metadata["device_class"] = ensure_str("device_class", metadata["device_class"])

		return await super().async_update_metadata(metadata)

	async def async_update_data(self, new_data: Dict[str, Any]) -> Dict[str, Any]:
		"""Validate and merge incoming data into the entity model.

        Accepted keys:
		- state: float
		- available: bool
		"""
		updated = dict(self.owl_model.data)

		if "state" in new_data:
			v = ensure_float("state", new_data["state"])
			ensure_in_range("state", v, self.native_min_value, self.native_max_value)
			updated["state"] = v

		self.owl_model.data = updated
		return await super().async_update_data(new_data)
