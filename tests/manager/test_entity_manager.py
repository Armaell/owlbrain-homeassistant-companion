from __future__ import annotations

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.owlbrain.manager.entity_manager import OwlBrainEntityManager
from custom_components.owlbrain.errors import (
    OwlDeviceNotFoundError,
    OwlEntityNotFoundError,
    OwlUnsupportedDomainError,
    OwlPlatformNotReadyError,
)
from custom_components.owlbrain.models.entity import EntityModel
from custom_components.owlbrain.utils.ids import build_unique_id_entity


@pytest.fixture
def hass():
    return MagicMock()


@pytest.fixture
def store():
    store = MagicMock()
    store.get_entities = AsyncMock(return_value={})
    store.get_entity = AsyncMock(return_value=None)
    store.set_entity = AsyncMock()
    store.save_entity = AsyncMock()
    store.save = AsyncMock()
    store.get_device = AsyncMock(return_value={"id": "dev1"})
    store.remove_entity = MagicMock()
    return store


@pytest.fixture
def manager():
    mgr = MagicMock()
    mgr.devices.cleanup_empty = AsyncMock()
    return mgr


@pytest.fixture
def entity_manager(hass, manager, store):
    return OwlBrainEntityManager(hass, manager, store)


@pytest.fixture
def mock_domain_handlers():
    """Patch DOMAIN_HANDLERS to control available domains."""
    with patch(
        "custom_components.owlbrain.domain.DOMAIN_HANDLERS",
        {"sensor": MagicMock()},
    ) as patched:
        yield patched


# -----------------------------
#region REGISTER_PLATFORM
# -----------------------------

def test_register_platform_stores_adder(entity_manager):
    # Arrange
    adder = MagicMock()

    # Act
    entity_manager.register_platform("sensor", adder)

    # Assert
    assert entity_manager.platform_adders["sensor"] is adder


# endregion -------------------
#region CREATE
# -----------------------------

@pytest.mark.asyncio
async def test_create_success(entity_manager, store, manager, mock_domain_handlers):
    # Arrange
    entity_manager.register_platform("sensor", MagicMock())
    store.get_entities.return_value = {}
    metadata = {"device_id": "dev1"}

    # Act
    model = await entity_manager.create("ns", "sensor.temp", metadata)

    # Assert
    assert model.namespace == "ns"
    assert model.entity_id == "sensor.temp"
    assert model.device_id == "dev1"
    store.set_entity.assert_awaited()
    manager.devices.cleanup_empty.assert_awaited()

@pytest.mark.asyncio
async def test_create_namespace_collision_raises(entity_manager, store, mock_domain_handlers):
    # Arrange
    entity_manager.register_platform("sensor", MagicMock())
    store.get_entities.return_value = {("other", "sensor.temp"): {}}

    # Act / Assert
    with pytest.raises(ValueError):
        await entity_manager.create("ns", "sensor.temp", {})


@pytest.mark.asyncio
async def test_create_platform_not_ready_raises(entity_manager, store, mock_domain_handlers):
    # Arrange
    store.get_entities.return_value = {}

    # Act / Assert
    with pytest.raises(OwlPlatformNotReadyError):
        await entity_manager.create("ns", "sensor.temp", {})


# endregion -------------------
#region UPDATE_METADATA
# -----------------------------

@pytest.mark.asyncio
async def test_update_metadata_success(entity_manager, store, mock_domain_handlers):
    # Arrange
    entity = EntityModel.from_dict(dict(
        namespace="ns",
        entity_id="sensor.temp",
        domain="sensor",
        unique_id="uid",
        metadata={},
        data={},
    ))
    store.get_entity.return_value = entity
    store.get_device.return_value = {"id": "dev1"}

    runtime = MagicMock()
    runtime.async_update_metadata = AsyncMock()
    entity_manager.runtime_entities["uid"] = runtime

    # Act
    model = await entity_manager.update_metadata("ns", "sensor.temp", {"device_id": "dev1"})

    # Assert
    assert model.device_id == "dev1"
    runtime.async_update_metadata.assert_awaited()


@pytest.mark.asyncio
async def test_update_metadata_missing_entity_raises(entity_manager, store):
    # Arrange
    store.get_entity.return_value = None

    # Act / Assert
    with pytest.raises(OwlEntityNotFoundError):
        await entity_manager.update_metadata("ns", "sensor.temp", {})


@pytest.mark.asyncio
async def test_update_metadata_missing_device_raises(entity_manager, store):
    # Arrange
    entity = EntityModel.from_dict(dict(
        namespace="ns",
        entity_id="sensor.temp",
        domain="sensor",
        unique_id="uid",
        metadata={},
        data={},
    ))
    store.get_entity.return_value = entity
    store.get_device.return_value = None

    # Act / Assert
    with pytest.raises(OwlDeviceNotFoundError):
        await entity_manager.update_metadata("ns", "sensor.temp", {"device_id": "missing"})


# endregion -------------------
#region UPDATE_DATA
# -----------------------------

@pytest.mark.asyncio
async def test_update_data_updates_runtime_and_store(entity_manager, store):
    # Arrange
    entity = EntityModel.from_dict(dict(
        namespace="ns",
        entity_id="sensor.temp",
        domain="sensor",
        unique_id="uid",
        metadata={},
        data={},
    ))
    store.get_entity.return_value = entity

    runtime = MagicMock()
    runtime.async_update_data = AsyncMock(return_value={"new": 1})
    entity_manager.runtime_entities["uid"] = runtime

    # Act
    model = await entity_manager.update_data("ns", "sensor.temp", {"a": 1})

    # Assert
    assert model.data == {"new": 1}
    store.save_entity.assert_awaited()


@pytest.mark.asyncio
async def test_update_data_missing_entity_raises(entity_manager, store):
    # Arrange
    store.get_entity.return_value = None

    # Act / Assert
    with pytest.raises(OwlEntityNotFoundError):
        await entity_manager.update_data("ns", "sensor.temp", {})


# endregion -------------------
#region DELETE
# -----------------------------

@pytest.mark.asyncio
async def test_delete_calls_cleanup_and_save(entity_manager, store, manager):
    # Arrange
    entity_manager.remove_entity_from_registries = AsyncMock()

    # Act
    await entity_manager.delete("ns", "sensor.temp")

    # Assert
    entity_manager.remove_entity_from_registries.assert_awaited()
    manager.devices.cleanup_empty.assert_awaited()
    store.save.assert_awaited()


# endregion -------------------
#region REMOVE_ENTITY_FROM_REGISTRIES
# -----------------------------

@pytest.mark.asyncio
async def test_remove_entity_from_registries_success(entity_manager, store):
    # Arrange
    entity = EntityModel.from_dict(dict(
        namespace="ns",
        entity_id="sensor.temp",
        domain="sensor",
        unique_id="uid"
    ))
    store.get_entity.return_value = entity

    runtime = MagicMock()
    runtime.async_remove = AsyncMock()
    entity_manager.runtime_entities["uid"] = runtime

    mock_registry = MagicMock()
    mock_registry.async_get_entity_id.return_value = "entity.sensor.temp"

    with patch(
        "custom_components.owlbrain.manager.entity_manager.er.async_get",
        return_value=mock_registry,
    ):
        # Act
        await entity_manager.remove_entity_from_registries("ns", "sensor.temp")

    # Assert
    mock_registry.async_remove.assert_called_once_with("entity.sensor.temp")
    runtime.async_remove.assert_awaited()
    store.remove_entity.assert_called_once()


@pytest.mark.asyncio
async def test_remove_entity_from_registries_missing_entity_raises(entity_manager, store):
    # Arrange
    store.get_entity.return_value = None

    # Act / Assert
    with pytest.raises(OwlEntityNotFoundError):
        await entity_manager.remove_entity_from_registries("ns", "sensor.temp")


# endregion -------------------
#region FORCE_HA_REFRESH
# -----------------------------

def test_force_ha_refresh_calls_write_state_only_for_namespace(entity_manager):
    # Arrange
    e1 = MagicMock()
    e1.owl_namespace = "ns"
    e2 = MagicMock()
    e2.owl_namespace = "other"

    entity_manager.runtime_entities = {"1": e1, "2": e2}

    # Act
    entity_manager.force_ha_refresh("ns")

    # Assert
    e1.async_write_ha_state.assert_called_once()
    e2.async_write_ha_state.assert_not_called()


# endregion
