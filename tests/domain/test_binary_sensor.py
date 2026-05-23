import pytest
from custom_components.owlbrain.domain.binary_sensor import OwlBrainBinarySensorEntity
from .helpers import EntityTestHelper
from custom_components.owlbrain.errors import OwlInvalidValueError
from custom_components.owlbrain.binary_sensor import async_setup_entry


@pytest.mark.asyncio
async def test_update_metadata(hass):
	helper = EntityTestHelper(
		OwlBrainBinarySensorEntity,
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
async def test_update_data(hass):
	helper = EntityTestHelper(
		OwlBrainBinarySensorEntity,
		hass=hass
	)

	await helper.run_data_matrix(
		[
			(
				"state",
				"on",
				None,
				{"is_on": True},
			),
			(
				"state",
				"off",
				None,
				{"is_on": False},
			),
			(
				"state",
				"invalid",
				OwlInvalidValueError,
				{"is_on": None},
			)
		]
	)


@pytest.mark.asyncio
async def test_light_platform_registration(hass):
    helper = EntityTestHelper(entity_cls=None, hass=hass, domain="binary_sensor")
    await helper.run_platform_registration_test(
        setup_fn=async_setup_entry
    )
