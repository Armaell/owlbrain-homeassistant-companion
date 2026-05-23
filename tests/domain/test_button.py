import pytest
from custom_components.owlbrain.domain.button import OwlBrainButtonEntity
from .helpers import EntityTestHelper
from custom_components.owlbrain.button import async_setup_entry

@pytest.mark.asyncio
async def test_update_metadata(hass):
	helper = EntityTestHelper(
		OwlBrainButtonEntity,
		hass=hass
	)

	await helper.run_metadata_matrix(
		[
			(
				"device_class",
				"foo",
				None,
				{"device_class": "foo"},
			)
		]
	)


@pytest.mark.asyncio
async def test_actions(hass):
	helper = EntityTestHelper(
		OwlBrainButtonEntity,
		hass=hass
	)
	await helper.run_action_matrix([
		(
			"async_press",
			None,
			"press",
			None,
		),
	])

@pytest.mark.asyncio
async def test_light_platform_registration(hass):
    helper = EntityTestHelper(entity_cls=None, hass=hass, domain="button")
    await helper.run_platform_registration_test(
        setup_fn=async_setup_entry
    )
