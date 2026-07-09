import pytest

from custom_components.owlbrain.cover import async_setup_entry
from custom_components.owlbrain.domain.cover import OwlBrainCoverEntity
from custom_components.owlbrain.errors import OwlInvalidValueError

from .helpers import EntityTestHelper


@pytest.mark.asyncio
async def test_update_metadata(hass):
	helper = EntityTestHelper(OwlBrainCoverEntity, hass=hass)

	await helper.run_metadata_matrix(
		[
			("", None, None, {"supported_features": 3}),
			("supported_features", 15, None, {"supported_features": 15}),
			(
				"supported_features",
				["open", "close", "set_position"],
				None,
				{"supported_features": 7},
			),
			(
				"supported_features",
				["open", "super ultra fast close"],
				OwlInvalidValueError,
				{"supported_features": 3},
			),
		]
	)


@pytest.mark.asyncio
async def test_update_data(hass):
	helper = EntityTestHelper(OwlBrainCoverEntity, hass=hass)

	await helper.run_data_matrix(
		[
			("state", "open", None, {"state": "open", "is_closed": False}),
			("state", "closed", None, {"state": "closed", "is_closed": True}),
			(
				"state",
				"opening",
				None,
				{"state": "opening", "is_closed": False},
			),
			(
				"state",
				"closing",
				None,
				{"state": "closing", "is_closed": False},
			),
			(
				"state",
				"invalid",
				OwlInvalidValueError,
				{"state": None, "is_closed": None},
			),
			("position", 21, None, {"current_cover_position": 21}),
			(
				"position",
				-21,
				OwlInvalidValueError,
				{"current_cover_position": None},
			),
			("tilt_position", 21, None, {"current_cover_tilt_position": 21}),
			(
				"tilt_position",
				-21,
				OwlInvalidValueError,
				{"current_cover_tilt_position": None},
			),
		]
	)


@pytest.mark.asyncio
async def test_actions(hass):
	helper = EntityTestHelper(OwlBrainCoverEntity, hass=hass)
	await helper.run_action_matrix(
		[
			("async_open_cover", None, "open", None),
			("async_open_cover_tilt", None, "open_tilt", None),
			("async_stop_cover", None, "stop", None),
			("async_close_cover", None, "close", None),
			("async_close_cover_tilt", None, "close_tilt", None),
			(
				"async_set_cover_position",
				{"position": 58},
				"set_position",
				{"position": 58},
			),
			(
				"async_set_cover_tilt_position",
				{"tilt_position": 58},
				"set_tilt_position",
				{"tilt_position": 58},
			),
		]
	)


@pytest.mark.asyncio
async def test_light_platform_registration(hass):
	helper = EntityTestHelper(entity_cls=None, hass=hass, domain="cover")
	await helper.run_platform_registration_test(setup_fn=async_setup_entry)
