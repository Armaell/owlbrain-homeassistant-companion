import pytest

from custom_components.owlbrain.domain.switch import OwlBrainSwitchEntity
from .helpers import EntityTestHelper
from custom_components.owlbrain.errors import OwlInvalidValueError
from custom_components.owlbrain.switch import async_setup_entry

@pytest.mark.asyncio
async def test_update_metadata(hass):
	helper = EntityTestHelper(
		OwlBrainSwitchEntity,
		hass=hass
	)

	await helper.run_metadata_matrix(
		[
			(
				"device_class",
				"outlet",
				None,
				{"device_class": "outlet"},
			)
		]
	)

@pytest.mark.asyncio
async def test_update_data(hass):
	helper = EntityTestHelper(
		OwlBrainSwitchEntity,
		hass=hass
	)

	await helper.run_data_matrix(
		[
			(
				"state",
				"on",
				None,
				{"state": "on", "is_on": True},
			),
			(
				"state",
				"off",
				None,
				{"state": "off", "is_on": False},
			),
			(
				"state",
				"invalid",
				OwlInvalidValueError,
				{"state": None},
			)
		]
	)


@pytest.mark.asyncio
async def test_actions(hass):
	helper = EntityTestHelper(
		OwlBrainSwitchEntity,
		hass=hass
	)
	await helper.run_action_matrix([
		(
			"async_turn_on",
			None,
			"turn_on",
			None,
		),
		(
			"async_turn_off",
			None,
			"turn_off",
			None,
		),
	])

@pytest.mark.asyncio
async def test_light_platform_registration(hass):
    helper = EntityTestHelper(entity_cls=None, hass=hass, domain="switch")
    await helper.run_platform_registration_test(
        setup_fn=async_setup_entry
    )
