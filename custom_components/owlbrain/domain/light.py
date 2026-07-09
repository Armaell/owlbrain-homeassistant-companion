from __future__ import annotations

from typing import Any

from homeassistant.components.light import ColorMode, LightEntity

from ..errors import OwlInvalidValueError
from ..utils.validation import (
	ensure_in_enum,
	ensure_in_list,
	ensure_in_range,
	ensure_int,
	ensure_str,
)
from .base import OwlBrainBaseEntity


class OwlBrainLightEntity(OwlBrainBaseEntity, LightEntity):
	"""Virtual OwlBrain Light."""

	def __init__(self, hass, manager, model) -> None:
		super().__init__(hass, manager, model)
		self._supported_color_modes = self._compute_supported_color_modes(
			model.metadata
		)

	# --------------------------
	# Basic state properties
	# --------------------------

	@property
	def is_on(self) -> bool | None:
		state = self.owl_model.data.get("state")
		return None if state is None else state == "on"

	@property
	def brightness(self) -> int | None:
		return self.owl_model.data.get("brightness")

	@property
	def color_temp(self) -> int | None:
		return self.owl_model.data.get("color_temp")

	@property
	def hs_color(self):
		hs = self.owl_model.data.get("hs_color")
		return tuple(hs) if hs else None

	@property
	def rgb_color(self):
		rgb = self.owl_model.data.get("rgb_color")
		return tuple(rgb) if rgb else None

	@property
	def rgbw_color(self):
		rgbw = self.owl_model.data.get("rgbw_color")
		return tuple(rgbw) if rgbw else None

	@property
	def rgbww_color(self):
		rgbww = self.owl_model.data.get("rgbww_color")
		return tuple(rgbww) if rgbww else None

	@property
	def xy_color(self):
		xy = self.owl_model.data.get("xy_color")
		return tuple(xy) if xy else None

	@property
	def white(self):
		return self.owl_model.data.get("white")

	@staticmethod
	def _compute_supported_color_modes(
		metadata: dict[str, Any],
	) -> set[ColorMode]:
		raw_modes = metadata.get("supported_color_modes", ["onoff"])
		return {ColorMode(mode) for mode in raw_modes}

	@property
	def supported_color_modes(self) -> set[ColorMode]:
		return self._supported_color_modes

	@property
	def color_mode(self) -> ColorMode:
		supported = self.supported_color_modes
		data = self.owl_model.data

		if len(supported) == 1:
			return next(iter(supported))

		modes = [
			("rgbww_color", ColorMode.RGBWW),
			("rgbw_color", ColorMode.RGBW),
			("rgb_color", ColorMode.RGB),
			("hs_color", ColorMode.HS),
			("xy_color", ColorMode.XY),
			("color_temp", ColorMode.COLOR_TEMP),
			("white", ColorMode.WHITE),
			("brightness", ColorMode.BRIGHTNESS),
			("state", ColorMode.ONOFF),
		]

		for key, mode in modes:
			if key in data and mode in supported:
				return mode

		if "state" in data and ColorMode.ONOFF in supported:
			return ColorMode.ONOFF

		return (
			ColorMode.ONOFF
			if ColorMode.ONOFF in supported
			else next(iter(supported))
		)

	async def async_turn_on(self, **kwargs: Any) -> None:
		payload: dict[str, Any] = {"state": "on"}

		color_keys = [
			"brightness",
			"color_temp",
			"hs_color",
			"xy_color",
			"rgb_color",
			"rgbw_color",
			"rgbww_color",
			"white",
		]

		for key in color_keys:
			if key in kwargs:
				value = kwargs[key]
				payload[key] = (
					list(value) if isinstance(value, tuple) else value
				)

		await self._broadcast_entity_action("turn_on", payload)

	async def async_turn_off(self, **kwargs: Any) -> None:
		await self._broadcast_entity_action("turn_off", {"state": "off"})

	async def async_update_metadata(
		self, metadata: dict[str, Any]
	) -> dict[str, Any]:
		normalized = await super().async_update_metadata(metadata)
		self._supported_color_modes = self._compute_supported_color_modes(
			normalized
		)
		return normalized

	@classmethod
	def validate_metadata(cls, metadata: dict[str, Any]) -> dict[str, Any]:
		"""Validate and normalize metadata.

		Accepted keys:
		- supported_color_modes: list[str] of "onoff" | "brightness" |
		  "color_temp" | "rgb" | "rgbw" | "rgbww" | "hs" | "xy" | "white"
		- any other base keys
		"""
		normalized = super().validate_metadata(metadata)

		if "supported_color_modes" in normalized:
			validated_modes = []
			for mode in normalized["supported_color_modes"]:
				mode_str = ensure_str("supported_color_modes", mode).lower()
				ensure_in_enum("supported_color_modes", mode_str, ColorMode)
				validated_modes.append(mode_str)

			normalized["supported_color_modes"] = validated_modes

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
		- brightness: 0-255
		- color_temp: int (mireds, > 0)
		- rgb_color: [r, g, b]
		- hs_color: [h, s]
		- available: bool
		"""
		updated = dict(current_data)

		def clear_color_modes():
			for key in (
				"hs_color",
				"xy_color",
				"rgb_color",
				"rgbw_color",
				"rgbww_color",
				"color_temp",
				"white",
			):
				updated.pop(key, None)

		if "state" in new_data:
			state = ensure_str("state", new_data["state"])
			ensure_in_list("state", state, {"on", "off"})
			updated["state"] = state

		if "brightness" in new_data:
			updated["brightness"] = ensure_in_range(
				"brightness",
				ensure_int("brightness", new_data["brightness"]),
				0,
				255,
			)

		if "color_temp" in new_data:
			ct = ensure_int("color_temp", new_data["color_temp"])
			if ct <= 0:
				raise OwlInvalidValueError("color_temp", ct, "above 0")
			clear_color_modes()
			updated["color_temp"] = ct

		if "hs_color" in new_data:
			hs = new_data["hs_color"]
			if not isinstance(hs, (list, tuple)) or len(hs) != 2:
				raise OwlInvalidValueError("hs_color", hs, "[h, s]")

			h, s = hs
			clear_color_modes()
			updated["hs_color"] = [
				ensure_in_range("hue", float(h), 0, 360),
				ensure_in_range("saturation", float(s), 0, 100),
			]

		if "xy_color" in new_data:
			x, y = new_data["xy_color"]
			clear_color_modes()
			updated["xy_color"] = [
				ensure_in_range("x", float(x), 0, 1),
				ensure_in_range("y", float(y), 0, 1),
			]

		if "rgb_color" in new_data:
			rgb = new_data["rgb_color"]
			if len(rgb) != 3:
				raise OwlInvalidValueError("rgb_color", rgb, "[r,g,b]")
			clear_color_modes()
			updated["rgb_color"] = [
				ensure_in_range("rgb", int(c), 0, 255) for c in rgb
			]

		if "rgbw_color" in new_data:
			rgbw = new_data["rgbw_color"]
			if len(rgbw) != 4:
				raise OwlInvalidValueError("rgbw_color", rgbw, "[r,g,b,w]")
			clear_color_modes()
			updated["rgbw_color"] = [
				ensure_in_range("rgbw", int(c), 0, 255) for c in rgbw
			]

		if "rgbww_color" in new_data:
			rgbww = new_data["rgbww_color"]
			if len(rgbww) != 5:
				raise OwlInvalidValueError(
					"rgbww_color", rgbww, "[r,g,b,cw,ww]"
				)
			clear_color_modes()
			updated["rgbww_color"] = [
				ensure_in_range("rgbww", int(c), 0, 255) for c in rgbww
			]

		if "white" in new_data:
			clear_color_modes()
			updated["white"] = ensure_in_range(
				"white", ensure_int("white", new_data["white"]), 0, 255
			)

		return super().validate_data(metadata, updated, new_data)
