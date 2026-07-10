import pytest
from homeassistant.components.light import ColorMode

from custom_components.owlbrain.domain.light import OwlBrainLightEntity
from custom_components.owlbrain.errors import OwlInvalidValueError
from custom_components.owlbrain.light import async_setup_entry

from .helpers import EntityTestHelper


@pytest.mark.asyncio
async def test_update_metadata(hass):
	helper = EntityTestHelper(OwlBrainLightEntity, hass=hass)

	await helper.run_metadata_matrix(
		[
			(
				"supported_color_modes",
				["rgb"],
				None,
				{"supported_color_modes": {ColorMode.RGB}},
			),
			(
				"supported_color_modes",
				["rgb", "hs"],
				None,
				{"supported_color_modes": {ColorMode.RGB, ColorMode.HS}},
			),
			(
				"supported_color_modes",
				["invalid"],
				OwlInvalidValueError,
				{"supported_color_modes": {ColorMode.ONOFF}},
			),
		]
	)


@pytest.mark.asyncio
async def test_update_data(hass):
	helper = EntityTestHelper(
		OwlBrainLightEntity,
		hass=hass,
		metadata={
			"supported_color_modes": {
				ColorMode.ONOFF,
				ColorMode.BRIGHTNESS,
				ColorMode.RGB,
				ColorMode.HS,
				ColorMode.COLOR_TEMP,
			}
		},
	)

	await helper.run_data_matrix(
		[
			("state", "on", None, {"state": "on", "is_on": True}),
			("state", "off", None, {"state": "off", "is_on": False}),
			("state", "invalid", OwlInvalidValueError, {"state": None}),
			(
				"brightness",
				120,
				None,
				{"brightness": 120, "color_mode": ColorMode.BRIGHTNESS},
			),
			("brightness", -1, OwlInvalidValueError, {}),
			(
				"rgb_color",
				[10, 20, 30],
				None,
				{"rgb_color": (10, 20, 30), "color_mode": ColorMode.RGB},
			),
			(
				"rgb_color",
				[1000, 20, 30],
				OwlInvalidValueError,
				{"rgb_color": None},
			),
			(
				"hs_color",
				[120, 50],
				None,
				{"hs_color": (120.0, 50.0), "color_mode": ColorMode.HS},
			),
			(
				"hs_color",
				[120, 5, 10],
				OwlInvalidValueError,
				{"hs_color": None},
			),
			(
				"color_temp_kelvin",
				4000,
				None,
				{"color_temp_kelvin": 4000, "color_mode": ColorMode.COLOR_TEMP},
			),
			(
				"color_temp_kelvin",
				-1,
				OwlInvalidValueError,
				{"color_temp_kelvin": None},
			),
			(
				"xy_color",
				[0.3, 0.4],
				None,
				{"xy_color": (0.3, 0.4)},
			),
			("xy_color", 123, OwlInvalidValueError, {"xy_color": None}),
			(
				"xy_color",
				[0.1, 0.2, 0.3],
				OwlInvalidValueError,
				{"xy_color": None},
			),
			("rgb_color", 123, OwlInvalidValueError, {"rgb_color": None}),
			(
				"rgbw_color",
				[10, 20, 30, 40],
				None,
				{"rgbw_color": (10, 20, 30, 40)},
			),
			("rgbw_color", 123, OwlInvalidValueError, {"rgbw_color": None}),
			(
				"rgbw_color",
				[10, 20, 30],
				OwlInvalidValueError,
				{"rgbw_color": None},
			),
			(
				"rgbww_color",
				[10, 20, 30, 40, 50],
				None,
				{"rgbww_color": (10, 20, 30, 40, 50)},
			),
			("rgbww_color", 123, OwlInvalidValueError, {"rgbww_color": None}),
			(
				"rgbww_color",
				[10, 20, 30, 40],
				OwlInvalidValueError,
				{"rgbww_color": None},
			),
		]
	)


@pytest.mark.asyncio
async def test_actions(hass):
	helper = EntityTestHelper(OwlBrainLightEntity, hass=hass)

	await helper.run_action_matrix(
		[
			(
				"async_turn_on",
				{"brightness": 100},
				"turn_on",
				{"state": "on", "brightness": 100},
			),
			(
				"async_turn_on",
				{"color_temp_kelvin": 4000},
				"turn_on",
				{"state": "on", "color_temp_kelvin": 4000},
			),
			(
				"async_turn_on",
				{"rgb_color": [10, 20, 30]},
				"turn_on",
				{"state": "on", "rgb_color": [10, 20, 30]},
			),
			(
				"async_turn_on",
				{"hs_color": [120, 50]},
				"turn_on",
				{"state": "on", "hs_color": [120, 50]},
			),
			("async_turn_off", {}, "turn_off", {"state": "off"}),
		]
	)


@pytest.mark.asyncio
async def test_light_platform_registration(hass):
	helper = EntityTestHelper(entity_cls=None, hass=hass, domain="light")
	await helper.run_platform_registration_test(setup_fn=async_setup_entry)
