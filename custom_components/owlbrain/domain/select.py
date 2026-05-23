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

	async def async_update_metadata(self, metadata: dict) -> None:
		"""Validate and overwrite metadata into the entity model.

		Accepted keys:
		- options: string array
		- any other base keys
		"""

		if "options" in metadata:
			if not isinstance(metadata["options"], list):
				raise OwlInvalidValueError("options", metadata["options"], "list of strings")
			if not all(isinstance(v, str) for v in metadata["options"]):
				raise OwlInvalidValueError("options", metadata["options"], "list of strings")

		return await super().async_update_metadata(metadata)

	async def async_update_data(self, new_data: Dict[str, Any]) -> Dict[str, Any]:
		"""Validate and merge incoming data into the entity model.

		Accepted keys:
		- state: a value from options
		- available: bool
		"""
		updated = dict(self.owl_model.data)

		if "state" in new_data:
			option = ensure_str("state", new_data["state"])
			ensure_in_list("state", option, self.options)
			updated["state"] = option

		self.owl_model.data = updated
		return await super().async_update_data(new_data)
