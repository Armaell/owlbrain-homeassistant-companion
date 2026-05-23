from __future__ import annotations

from typing import Any, Dict

from homeassistant.components.button import ButtonEntity

from .base import OwlBrainBaseEntity
from ..utils.validation import ensure_str


class OwlBrainButtonEntity(OwlBrainBaseEntity, ButtonEntity):

	@property
	def device_class(self) -> str | None:
		return self.owl_model.metadata.get("device_class")

	async def async_press(self) -> None:
		await self._broadcast_entity_action("press", None)

	async def async_update_metadata(self, metadata: dict) -> None:
		"""Validate and overwrite metadata into the entity model.

		Accepted keys:
		- device_class: str
		"""

		if "device_class" in metadata:
			dc = ensure_str("device_class", metadata["device_class"])
			metadata["device_class"] = dc

		return await super().async_update_metadata(metadata)
