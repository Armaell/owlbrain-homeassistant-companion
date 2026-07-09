from unittest.mock import MagicMock

import pytest

from custom_components.owlbrain.domain.base import OwlBrainBaseEntity

from .helpers import EntityTestHelper


@pytest.fixture
def mock_broadcaster():
	broadcaster = MagicMock()
	broadcaster.available.return_value = True
	return broadcaster


@pytest.fixture
def mock_manager(mock_broadcaster):
	manager = MagicMock()
	manager.broadcaster = mock_broadcaster
	return manager


@pytest.mark.asyncio
async def test_update_metadata(hass, mock_manager):
	helper = EntityTestHelper(
		OwlBrainBaseEntity, hass=hass, manager=mock_manager
	)

	await helper.run_metadata_matrix(
		[
			("name", "Name", None, {"name": "Name"}),
			("entity_category", "cat", None, {"entity_category": "cat"}),
			("icon", "cat", None, {"icon": "cat"}),
			("translation_key", "es", None, {"translation_key": "es"}),
			("entity_picture", "cat", None, {"entity_picture": "cat"}),
		]
	)


@pytest.mark.asyncio
async def test_update_data(hass, mock_manager):
	helper = EntityTestHelper(
		OwlBrainBaseEntity, hass=hass, manager=mock_manager
	)

	await helper.run_data_matrix(
		[
			("available", True, None, {"available": True}),
			("available", False, None, {"available": False}),
		]
	)


def test_is_unavailable_when_no_active_connection(hass, mock_manager):
	entity = EntityTestHelper(
		OwlBrainBaseEntity, hass=hass, manager=mock_manager
	).create_entity()

	mock_manager.broadcaster.available.return_value = True
	assert entity.available

	mock_manager.broadcaster.available.return_value = False
	assert not entity.available


@pytest.mark.asyncio
async def test_device_info_none_when_no_device_id(hass, mock_manager):
	entity = EntityTestHelper(
		OwlBrainBaseEntity, hass=hass, manager=mock_manager, metadata={}
	).create_entity()

	assert entity.device_info is None


@pytest.mark.asyncio
async def test_device_info_none_when_device_not_found(hass, mock_manager):
	entity = EntityTestHelper(
		OwlBrainBaseEntity,
		hass=hass,
		manager=mock_manager,
		metadata={"device_id": "dev123"},
	).create_entity()

	mock_manager.store = MagicMock()
	mock_manager.store.sync_get_device.return_value = None

	assert entity.device_info is None


@pytest.mark.asyncio
async def test_device_info_returns_expected_structure(hass, mock_manager):
	entity = EntityTestHelper(
		OwlBrainBaseEntity,
		hass=hass,
		manager=mock_manager,
		metadata={"device_id": "dev123"},
	).create_entity()

	mock_device = MagicMock()
	mock_device.unique_id = "dev123"
	mock_device.metadata = {
		"connections": [("mac", "AA:BB:CC:DD:EE:FF")],
		"manufacturer": "OwlCorp",
		"model": "OwlModelX",
		"name": "Owl Device",
		"sw_version": "1.2.3",
		"hw_version": "revA",
		"serial_number": "SN123",
		"via_device": "hub1",
		"suggested_area": "Living Room",
		"configuration_url": "https://config.owl",
	}

	mock_manager.store = MagicMock()
	mock_manager.store.sync_get_device.return_value = mock_device

	info = entity.device_info

	assert info["identifiers"] == {("owlbrain", "dev123")}
	assert info["connections"] == [("mac", "AA:BB:CC:DD:EE:FF")]
	assert info["manufacturer"] == "OwlCorp"
	assert info["model"] == "OwlModelX"
	assert info["name"] == "Owl Device"
	assert info["sw_version"] == "1.2.3"
	assert info["hw_version"] == "revA"
	assert info["serial_number"] == "SN123"
	assert info["via_device"] == "hub1"
	assert info["suggested_area"] == "Living Room"
	assert info["configuration_url"] == "https://config.owl"
