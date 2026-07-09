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

	@classmethod
	def validate_metadata(cls, metadata: dict) -> dict:
		"""Validate and normalize metadata.

		Accepted keys:
		- device_class: str
		"""
		normalized = super().validate_metadata(metadata)

		if "device_class" in normalized:
			normalized["device_class"] = ensure_str("device_class", normalized["device_class"])

		return normalized
