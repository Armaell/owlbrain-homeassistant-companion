from __future__ import annotations

from typing import Any, Dict, Optional

from homeassistant.components.cover import (
    CoverEntity,
    CoverEntityFeature
)


from .base import OwlBrainBaseEntity
from ..utils.validation import ensure_int, ensure_str, ensure_in_range, ensure_features_flag, ensure_in_list


class OwlBrainCoverEntity(OwlBrainBaseEntity, CoverEntity):

	@property
	def state(self) -> Optional[str]:
		return self.owl_model.data.get("state")

	@property
	def supported_features(self) -> int:
		return self.owl_model.metadata.get("supported_features", 3)

	@property
	def is_closed(self) -> Optional[bool]:
		state = self.owl_model.data.get("state")
		if state is None:
			return None
		if state == "closed":
			return True
		return False

	@property
	def current_cover_position(self) -> Optional[int]:
		return self.owl_model.data.get("position")

	@property
	def current_cover_tilt_position(self) -> Optional[int]:
		return self.owl_model.data.get("tilt_position")

	async def async_open_cover(self, **kwargs: Any) -> None:
		await self._broadcast_entity_action(
			"open", None
		)

	async def async_open_cover_tilt(self, **kwargs: Any) -> None:
		await self._broadcast_entity_action(
			"open_tilt", None
		)

	async def async_stop_cover(self, **kwargs: Any) -> None:
		await self._broadcast_entity_action(
			"stop", None
		)

	async def async_close_cover(self, **kwargs: Any) -> None:
		await self._broadcast_entity_action(
			"close", None
		)

	async def async_close_cover_tilt(self, **kwargs: Any) -> None:
		await self._broadcast_entity_action(
			"close_tilt", None
		)

	async def async_set_cover_position(self, **kwargs: Any) -> None:
		position = kwargs.get("position")
		await self._broadcast_entity_action(
			"set_position", {"position": position}
		)

	async def async_set_cover_tilt_position(self, **kwargs: Any) -> None:
		tilt = kwargs.get("tilt_position")
		await self._broadcast_entity_action(
			"set_tilt_position", {"tilt_position": tilt}
		)

	@classmethod
	def validate_metadata(cls, metadata: dict) -> dict:
		"""Validate and normalize metadata.

		Accepted keys:
		- supported_features: int | list[str]
		- any other base keys
		"""
		normalized = super().validate_metadata(metadata)

		if "supported_features" in normalized:
			normalized["supported_features"] = ensure_features_flag(
				"supported_features",
				normalized["supported_features"],
				CoverEntityFeature,
			)

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
		- state: "open" | "closed" | "opening" | "closing"
		- position: 0-100
		- tilt_position: 0-100
		- available: bool
        """
		updated = dict(current_data)

		if "state" in new_data:
			state = ensure_str("state", new_data["state"])
			ensure_in_list("state", state, {"open", "closed", "opening", "closing"})
			updated["state"] = state

		if "position" in new_data:
			pos = ensure_int("position", new_data["position"])
			ensure_in_range("position", pos, 0, 100)
			updated["position"] = pos

		if "tilt_position" in new_data:
			tilt = ensure_int("tilt_position", new_data["tilt_position"])
			ensure_in_range("tilt_position", tilt, 0, 100)
			updated["tilt_position"] = tilt

		return super().validate_data(metadata, updated, new_data)
