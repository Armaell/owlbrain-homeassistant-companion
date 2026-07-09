from __future__ import annotations

from typing import Any

from homeassistant.components.number import NumberEntity, NumberMode

from ..utils.validation import (
	ensure_float,
	ensure_in_enum,
	ensure_in_range,
	ensure_str,
)
from .base import OwlBrainBaseEntity


class OwlBrainNumberEntity(OwlBrainBaseEntity, NumberEntity):
	@property
	def native_value(self) -> float | None:
		state = self.owl_model.data.get("state")
		return self.native_min_value if state is None else float(state)

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
	def unit_of_measurement(self) -> str | None:
		return self.owl_model.metadata.get("unit")

	@property
	def device_class(self) -> str | None:
		return self.owl_model.metadata.get("device_class")

	async def async_set_native_value(self, value: float) -> None:
		await self._broadcast_entity_action("set_state", {"state": value})

	@classmethod
	def validate_metadata(cls, metadata: dict) -> dict:
		"""Validate and normalize metadata.

		Accepted keys:
		- min: float
		- max: float
		- step: float
		- mode: "auto" | "box" | "slider"
		- unit: str
		- device_class: str
		- any other base keys
		"""
		normalized = super().validate_metadata(metadata)

		if "min" in normalized:
			normalized["min"] = ensure_float("min", normalized["min"])

		if "max" in normalized:
			normalized["max"] = ensure_float("max", normalized["max"])

		if "step" in normalized:
			normalized["step"] = ensure_float("step", normalized["step"])

		if "mode" in normalized:
			mode = ensure_str("mode", normalized["mode"])
			ensure_in_enum("mode", mode, NumberMode)
			normalized["mode"] = mode

		if "unit" in normalized:
			normalized["unit"] = ensure_str("unit", normalized["unit"])

		if "device_class" in normalized:
			normalized["device_class"] = ensure_str(
				"device_class", normalized["device_class"]
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
		        - state: float
		        - available: bool
		"""
		updated = dict(current_data)

		if "state" in new_data:
			v = ensure_float("state", new_data["state"])
			native_min = float(metadata.get("min", 0))
			native_max = float(metadata.get("max", 100))
			ensure_in_range("state", v, native_min, native_max)
			updated["state"] = v

		return super().validate_data(metadata, updated, new_data)
