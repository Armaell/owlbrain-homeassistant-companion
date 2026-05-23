import pytest

from custom_components.owlbrain.domain.select import OwlBrainSelectEntity
from .helpers import EntityTestHelper
from custom_components.owlbrain.errors import OwlInvalidValueError
from custom_components.owlbrain.select import async_setup_entry


@pytest.mark.asyncio
async def test_update_metadata(hass):
	helper = EntityTestHelper(
		OwlBrainSelectEntity,
		hass=hass
	)

	await helper.run_metadata_matrix(
		[
			(
				"options",
				["a", "b"],
				None,
				{"options": ["a", "b"]},
			),
			(
				"options",
				"invalid",
				OwlInvalidValueError,
				{"options": []},
			),
		]
	)


@pytest.mark.asyncio
async def test_update_data(hass):
	helper = EntityTestHelper(
		OwlBrainSelectEntity,
		hass=hass,
		metadata={"options": ["a", "b"]}
	)

	await helper.run_data_matrix(
		[
			(
				"state",
				"a",
				None,
				{"current_option": "a"},
			),
			(
				"state",
				"c",
				OwlInvalidValueError,
				{"current_option": None},
			)
		]
	)


@pytest.mark.asyncio
async def test_actions(hass):
	helper = EntityTestHelper(
		OwlBrainSelectEntity,
		hass=hass,
		metadata={"options": ["a", "b"]}
	)
	await helper.run_action_matrix([
		(
			"async_select_option",
			("b",),
			"select",
			{"state": "b"},
		)
	])

@pytest.mark.asyncio
async def test_light_platform_registration(hass):
    helper = EntityTestHelper(entity_cls=None, hass=hass, domain="select")
    await helper.run_platform_registration_test(
        setup_fn=async_setup_entry
    )
