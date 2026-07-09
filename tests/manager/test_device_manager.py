from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.helpers import device_registry as dr

from custom_components.owlbrain.errors import (
	OwlDeviceNotFoundError,
	OwlNamespaceCollisionError,
)
from custom_components.owlbrain.manager.device_manager import (
	OwlBrainDeviceManager,
)
from custom_components.owlbrain.models.device import DeviceModel
from custom_components.owlbrain.models.entity import EntityModel


@pytest.fixture
def mock_store():
	store = AsyncMock()
	store.get_devices.return_value = {}
	store.get_entities.return_value = {}
	return store


@pytest.fixture
def mock_entity_manager():
	return AsyncMock()


@pytest.fixture
def mock_manager():
	mgr = MagicMock()
	mgr.hass = MagicMock()
	return mgr


@pytest.fixture
def device_manager(mock_manager, mock_entity_manager, mock_store):
	return OwlBrainDeviceManager(
		manager=mock_manager,
		entity_manager=mock_entity_manager,
		store=mock_store,
	)


# -----------------------------
# region CREATE
# -----------------------------


@pytest.mark.asyncio
async def test_create_new_device(device_manager, mock_store):
	# Arrange
	mock_store.get_devices.return_value = {}
	mock_store.get_device.return_value = None
	metadata = {"name": "Lamp"}

	# Act
	result = await device_manager.create("ns1", "dev1", metadata)

	# Assert
	assert result.namespace == "ns1"
	assert result.device_id == "dev1"
	assert result.metadata == metadata
	mock_store.save_device.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_raises_on_namespace_collision(device_manager, mock_store):
	# Arrange
	mock_store.get_devices.return_value = {
		("nsX", "dev1"): DeviceModel.from_dict({})
	}
	mock_store.get_device.return_value = None

	# Act / Assert
	with pytest.raises(OwlNamespaceCollisionError):
		await device_manager.create("ns1", "dev1", {"meta": 1})


# endregion -------------------
# region UPDATE
# -----------------------------


@pytest.mark.asyncio
async def test_update(device_manager, mock_store):
	# Arrange
	existing = DeviceModel(
		namespace="ns1",
		device_id="dev1",
		metadata={"old": True},
		unique_id="uid123",
	)
	mock_store.get_device.return_value = existing
	metadata = {"new": True}

	# Act
	result = await device_manager.update("ns1", "dev1", metadata)

	# Assert
	assert result.metadata == metadata
	mock_store.save_device.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_raises_if_not_found(device_manager, mock_store):
	# Arrange
	mock_store.get_device.return_value = None

	# Act / Assert
	with pytest.raises(OwlDeviceNotFoundError):
		await device_manager.update("ns1", "dev1", {"new": True})


# endregion -------------------
# region UPSERT
# -----------------------------


@pytest.mark.asyncio
async def test_upsert_creates_when_missing(device_manager, mock_store):
	# Arrange
	mock_store.get_devices.return_value = {}
	mock_store.get_device.return_value = None
	metadata = {"name": "Lamp"}

	# Act
	device, action = await device_manager.upsert("ns1", "dev1", metadata)

	# Assert
	assert action == "created"
	assert device.metadata == metadata


@pytest.mark.asyncio
async def test_upsert_updates_when_existing(device_manager, mock_store):
	# Arrange
	existing = DeviceModel(
		namespace="ns1",
		device_id="dev1",
		metadata={"old": True},
		unique_id="uid123",
	)
	mock_store.get_device.return_value = existing
	metadata = {"new": True}

	# Act
	device, action = await device_manager.upsert("ns1", "dev1", metadata)

	# Assert
	assert action == "updated"
	assert device.metadata == metadata


# endregion -------------------
# region DELETE
# -----------------------------


@pytest.mark.asyncio
async def test_delete_raises_if_not_found(device_manager, mock_store):
	# Arrange
	mock_store.get_device.return_value = None

	# Act / Assert
	with pytest.raises(OwlDeviceNotFoundError):
		await device_manager.delete("ns1", "dev1")


@pytest.mark.asyncio
async def test_delete_removes_entities_and_device(
	device_manager, mock_store, mock_entity_manager
):
	# Arrange
	device = DeviceModel.from_dict(
		{"namespace": "ns1", "device_id": "dev1", "unique_id": "uid1"}
	)
	mock_store.get_device.return_value = device
	mock_store.get_entities.return_value = {
		("ns1", "e1"): EntityModel.from_dict(
			{"metadata": {"device_id": "dev1"}, "namespace": "ns1"}
		),
		("ns1", "e2"): EntityModel.from_dict(
			{"metadata": {"device_id": "dev1"}, "namespace": "ns1"}
		),
		("ns1", "other"): EntityModel.from_dict(
			{"metadata": {"device_id": "devX"}, "namespace": "ns1"}
		),
	}

	mock_registry = MagicMock()
	mock_registry.async_get_device = MagicMock(
		return_value=MagicMock(id="reg1")
	)
	mock_registry.async_remove_device = AsyncMock()

	with patch.object(dr, "async_get", return_value=mock_registry):
		# Act
		await device_manager.delete("ns1", "dev1")

	# Assert
	assert (
		mock_entity_manager._remove_entity_from_registries_locked.await_count
		== 2
	)
	mock_store.remove_device.assert_called_once_with(device)
	mock_store.save.assert_awaited_once()
	mock_registry.async_remove_device.assert_awaited_once_with("reg1")


# endregion -------------------
# region CLEANUP EMPTY
# -----------------------------


@pytest.mark.asyncio
async def test_cleanup_empty_deletes_devices_without_entities(
	device_manager, mock_store
):
	# Arrange
	dev1 = DeviceModel.from_dict({"namespace": "ns1", "device_id": "d1"})
	dev2 = DeviceModel.from_dict({"namespace": "ns1", "device_id": "d2"})
	dev3 = DeviceModel.from_dict({"namespace": "nsX", "device_id": "d3"})
	e1 = EntityModel.from_dict(
		{"namespace": "ns1", "metadata": {"device_id": "d2"}}
	)
	mock_store.get_devices.return_value = {
		("ns1", "d1"): dev1,
		("ns1", "d2"): dev2,
		("nsX", "d3"): dev3,
	}
	mock_store.get_entities.return_value = {("ns1", "e1"): e1}

	mock_registry = MagicMock()
	mock_registry.async_remove_device = AsyncMock()

	device_manager._delete_locked = AsyncMock()

	with patch.object(dr, "async_get", return_value=mock_registry):
		# Act
		await device_manager.cleanup_empty("ns1")

	# Assert
	device_manager._delete_locked.assert_awaited_once_with("ns1", "d1")


@pytest.mark.asyncio
async def test_cleanup_empty_no_action_when_all_have_entities(
	device_manager, mock_store
):
	# Arrange
	mock_store.get_devices.return_value = {
		("ns1", "d1"): DeviceModel.from_dict(
			{"namespace": "ns1", "device_id": "d1"}
		)
	}
	mock_store.get_entities.return_value = {
		("ns1", "e1"): EntityModel.from_dict(
			{"namespace": "ns1", "metadata": {"device_id": "d1"}}
		)
	}

	device_manager.delete = AsyncMock()

	# Act
	await device_manager.cleanup_empty("ns1")

	# Assert
	device_manager.delete.assert_not_awaited()


# endregion
