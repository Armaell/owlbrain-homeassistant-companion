from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity

from ..utils.validation import ensure_in_list, ensure_str
from .base import OwlBrainBaseEntity


class OwlBrainSwitchEntity(OwlBrainBaseEntity, SwitchEntity):
	@property
	def is_on(self) -> bool | None:
		state = self.owl_model.data.get("state")
		if state is None:
			return None
		return state == "on"

	@property
	def device_class(self) -> str | None:
		return self.owl_model.metadata.get("device_class")

	async def async_turn_on(self, **kwargs: Any) -> None:
		await self._broadcast_entity_action("turn_on", None)

	async def async_turn_off(self, **kwargs: Any) -> None:
		await self._broadcast_entity_action("turn_off", None)

	@classmethod
	def validate_metadata(cls, metadata: dict) -> dict:
		"""Validate and normalize metadata.

		Accepted keys:
		- device_class: str
		- any other base keys
		"""
		normalized = super().validate_metadata(metadata)

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
		- state: "on" | "off"
		- available: bool
		"""
		updated = dict(current_data)

		if "state" in new_data:
			state = ensure_str("state", new_data["state"])
			ensure_in_list("state", state, {"on", "off"})
			updated["state"] = state

		return super().validate_data(metadata, updated, new_data)
