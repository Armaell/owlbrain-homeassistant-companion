from __future__ import annotations

from typing import Any, Dict, Optional, List

from homeassistant.components.select import SelectEntity

from .base import OwlBrainBaseEntity
from ..errors import OwlInvalidValueError
from ..utils.validation import ensure_str, ensure_in_list


class OwlBrainSelectEntity(OwlBrainBaseEntity, SelectEntity):

	@property
	def current_option(self) -> Optional[str]:
		return self.owl_model.data.get("state")

	@property
	def options(self) -> List[str]:
		return self.owl_model.metadata.get("options", [])

	async def async_select_option(self, option: str) -> None:
		await self._broadcast_entity_action("select", { "state": option })

	@classmethod
	def validate_metadata(cls, metadata: dict) -> dict:
		"""Validate and normalize metadata.

		Accepted keys:
		- options: string array
		- any other base keys
		"""
		normalized = super().validate_metadata(metadata)

		if "options" in normalized:
			if not isinstance(normalized["options"], list):
				raise OwlInvalidValueError("options", normalized["options"], "list of strings")
			if not all(isinstance(v, str) for v in normalized["options"]):
				raise OwlInvalidValueError("options", normalized["options"], "list of strings")

		return normalized

	@classmethod
	def validate_data(
		cls,
		metadata: Dict[str, Any],
		current_data: Dict[str, Any],
		new_data: Dict[str, Any],
	) -> Dict[str, Any]:
		"""Validate and merge incoming data.

		Accepted keys:
		- state: a value from options
		- available: bool
		"""
		updated = dict(current_data)

		if "state" in new_data:
			option = ensure_str("state", new_data["state"])
			ensure_in_list("state", option, metadata.get("options", []))
			updated["state"] = option

		return super().validate_data(metadata, updated, new_data)
