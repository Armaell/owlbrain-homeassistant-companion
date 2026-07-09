# test_light.py

import pytest
from custom_components.owlbrain.domain.sensor import OwlBrainSensorEntity
from .helpers import EntityTestHelper
from custom_components.owlbrain.errors import OwlInvalidValueError
from custom_components.owlbrain.sensor import async_setup_entry


@pytest.mark.asyncio
async def test_update_metadata(hass):
	helper = EntityTestHelper(
		OwlBrainSensorEntity,
		hass=hass
	)

	await helper.run_metadata_matrix(
		[
			(
				"unit",
				"unit",
				None,
				{"native_unit_of_measurement": "unit"},
			),
			(
				"device_class",
				"battery",
				None,
				{"device_class": "battery"},
			),
			(
				"device_class",
				"invalid",
				OwlInvalidValueError,
				{"device_class": None},
			),
			(
				"state_class",
				"measurement",
				None,
				{"state_class": "measurement"},
			),
			(
				"state_class",
				"invalid",
				OwlInvalidValueError,
				{"state_class": None},
			)
		]
	)


@pytest.mark.asyncio
async def test_update_data(hass):
	helper = EntityTestHelper(
		OwlBrainSensorEntity,
		hass=hass
	)

	await helper.run_data_matrix(
		[
			(
				"state",
				"on",
				None,
				{"native_value": "on"},
			)
		]
	)

@pytest.mark.asyncio
async def test_light_platform_registration(hass):
    helper = EntityTestHelper(entity_cls=None, hass=hass, domain="sensor")
    await helper.run_platform_registration_test(
        setup_fn=async_setup_entry
    )
