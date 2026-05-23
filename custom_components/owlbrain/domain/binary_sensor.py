from __future__ import annotations

from typing import Any, Dict, Optional

from homeassistant.components.binary_sensor import BinarySensorEntity

from .base import OwlBrainBaseEntity
from ..utils.validation import ensure_str, ensure_in_list


class OwlBrainBinarySensorEntity(OwlBrainBaseEntity, BinarySensorEntity):
	@property
	def is_on(self) -> Optional[bool]:
		state = self.owl_model.data.get("state")
		if state is None:
			return None
		return state == "on"

	@property
	def device_class(self) -> Optional[str]:
		return self.owl_model.metadata.get("device_class")


	async def async_update_metadata(self, metadata: dict) -> None:
		"""Validate and overwrite metadata into the entity model.

		Accepted keys:
		- device_class: str
		- any other base keys
		"""

		if "device_class" in metadata:
			dc = ensure_str("device_class", metadata["device_class"])
			metadata["device_class"] = dc

		return await super().async_update_metadata(metadata)

	async def async_update_data(self, new_data: Dict[str, Any]) -> Dict[str, Any]:
		"""Validate and merge incoming data into the entity model.

		Accepted keys:
		- state: "on" | "off"
		- available: bool
		"""
		updated = dict(self.owl_model.data)

		if "state" in new_data:
			state = ensure_str("state", new_data["state"])
			ensure_in_list("state", state, {"on", "off"})
			updated["state"] = state

		self.owl_model.data = updated
		return await super().async_update_data(new_data)
