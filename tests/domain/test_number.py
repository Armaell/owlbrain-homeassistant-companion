import pytest

from custom_components.owlbrain.domain.number import OwlBrainNumberEntity
from custom_components.owlbrain.errors import OwlInvalidValueError
from custom_components.owlbrain.number import async_setup_entry

from .helpers import EntityTestHelper


@pytest.mark.asyncio
async def test_update_metadata(hass):
	helper = EntityTestHelper(OwlBrainNumberEntity, hass=hass)

	await helper.run_metadata_matrix(
		[
			("min", 12, None, {"native_min_value": 12}),
			("min", "min", OwlInvalidValueError, {}),
			("max", 12, None, {"native_max_value": 12}),
			("max", "max", OwlInvalidValueError, {}),
			("step", 12, None, {"native_step": 12}),
			("step", "step", OwlInvalidValueError, {}),
			("mode", "auto", None, {"mode": "auto"}),
			("mode", "slider", None, {"mode": "slider"}),
			("mode", "mode", OwlInvalidValueError, {}),
			("unit", "unit", None, {"unit_of_measurement": "unit"}),
			(
				"device_class",
				"device_class",
				None,
				{"device_class": "device_class"},
			),
		]
	)


@pytest.mark.asyncio
async def test_update_data(hass):
	min_value = 10
	max_value = 20
	helper = EntityTestHelper(
		OwlBrainNumberEntity,
		hass=hass,
		metadata={"min": min_value, "max": max_value},
	)

	await helper.run_data_matrix(
		[
			("state", 15, None, {"native_value": 15}),
			(
				"state",
				min_value - 1,
				OwlInvalidValueError,
				{"native_value": min_value},
			),
			(
				"state",
				max_value + 1,
				OwlInvalidValueError,
				{"native_value": min_value},
			),
		]
	)


@pytest.mark.asyncio
async def test_actions(hass):
	helper = EntityTestHelper(OwlBrainNumberEntity, hass=hass)
	await helper.run_action_matrix(
		[("async_set_native_value", (3,), "set_state", {"state": 3})]
	)


@pytest.mark.asyncio
async def test_light_platform_registration(hass):
	helper = EntityTestHelper(entity_cls=None, hass=hass, domain="number")
	await helper.run_platform_registration_test(setup_fn=async_setup_entry)
