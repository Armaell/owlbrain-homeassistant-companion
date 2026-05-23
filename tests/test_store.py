import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock

from homeassistant.core import HomeAssistant

from custom_components.owlbrain.store import OwlBrainStore
from custom_components.owlbrain.models.device import DeviceModel
from custom_components.owlbrain.models.entity import EntityModel


# ---------------------------------------------------------------------------
#region Helpers
# ---------------------------------------------------------------------------

@pytest.fixture
def store(hass):
    """Create OwlBrainStore with mocked storage backend."""
    store = OwlBrainStore(hass)

    # Patch the internal Store object
    store._store = MagicMock()
    store._store.async_load = AsyncMock(return_value=None)
    store._store.async_save = AsyncMock()

    return store


#endregion ------------------------------------------------------------------
#region Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_initial_load_empty(store):
    await store._ensure_loaded()
    assert store._devices == {}
    assert store._entities == {}


@pytest.mark.asyncio
async def test_load_existing_data(store):
    store._store.async_load.return_value = {
        "devices": [
            {"namespace": "ns", "device_id": "dev1", "value": "A"},
        ],
        "entities": [
            {"namespace": "ns", "entity_id": "ent1", "value": "B"},
        ],
    }

    await store._ensure_loaded()

    assert ("ns", "dev1") in store._devices
    assert ("ns", "ent1") in store._entities


@pytest.mark.asyncio
async def test_set_and_get_device(store):
    await store._ensure_loaded()

    dev = DeviceModel.from_dict({"namespace":"ns", "device_id":"dev1", "metadata":"D"})
    await store.set_device(dev)

    result = await store.get_device("ns", "dev1")
    assert result.metadata == "D"


@pytest.mark.asyncio
async def test_set_and_get_entity(store):
    await store._ensure_loaded()

    ent = EntityModel.from_dict({"namespace":"ns", "entity_id":"ent1", "data":"D"})
    await store.set_entity(ent)

    result = await store.get_entity("ns", "ent1")
    assert result.data == "D"


@pytest.mark.asyncio
async def test_save_calls_async_save(store):
    await store._ensure_loaded()

    dev = DeviceModel.from_dict({"namespace":"ns", "device_id":"dev1"})
    ent = EntityModel.from_dict({"namespace":"ns", "entity_id":"ent1", "data":"D"})

    await store.set_device(dev)
    await store.set_entity(ent)

    await store.save()

    store._store.async_save.assert_called_once()
    saved_data = store._store.async_save.call_args[0][0]

    assert saved_data["devices"][0]["device_id"] == "dev1"
    assert saved_data["entities"][0]["entity_id"] == "ent1"


@pytest.mark.asyncio
async def test_remove_device(store):
    await store._ensure_loaded()

    dev = DeviceModel.from_dict({"namespace":"ns", "device_id":"dev1"})
    await store.set_device(dev)

    store.remove_device(dev)
    assert ("ns", "dev1") not in store._devices


@pytest.mark.asyncio
async def test_remove_entity(store):
    await store._ensure_loaded()

    ent = EntityModel.from_dict({"namespace":"ns", "entity_id":"ent1"})
    await store.set_entity(ent)

    store.remove_entity(ent)
    assert ("ns", "ent1") not in store._entities

#endregion