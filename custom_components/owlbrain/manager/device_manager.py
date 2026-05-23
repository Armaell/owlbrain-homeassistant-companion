from __future__ import annotations

import asyncio
import logging

from homeassistant.helpers import device_registry as dr

from ..errors import OwlDeviceNotFoundError
from ..store import OwlBrainStore
from .entity_manager import OwlBrainEntityManager
from ..utils.ids import build_unique_id_device
from ..const import DOMAIN
from ..models.device import DeviceModel

_LOGGER = logging.getLogger(__name__)

class OwlBrainDeviceManager:
	def __init__(self, manager, entity_manager: OwlBrainEntityManager, store: OwlBrainStore):
		self._lock = asyncio.Lock()
		self.manager = manager
		self.entity_manager = entity_manager
		self.store = store

	async def create(self, namespace: str, device_id: str, metadata: dict) -> DeviceModel:
		"""Create a device"""
		async with self._lock:
			devices = await self.store.get_devices()

			# Check for namespace collision
			for (ns, did) in devices.keys():
				if did == device_id and ns != namespace:
					raise ValueError("Device already exists in another namespace")

			device = DeviceModel(
				namespace=namespace,
				device_id=device_id,
				metadata=metadata,
				unique_id=build_unique_id_device(namespace, device_id),
			)

			await self.store.save_device(device)
			_LOGGER.info("Created device %s", device_id)
			return device

	async def update(self, namespace: str, device_id: str, metadata: dict) -> DeviceModel:
		"""Update a device by overwriting its metadata"""
		async with self._lock:
			device = await self.store.get_device(namespace, device_id)

			device.metadata = metadata

			await self.store.save_device(device)
			_LOGGER.debug("Updated device %s's metadata", device_id)
			return device

	async def delete(self, namespace: str, device_id: str) -> None:
		async with self._lock:
			device = await self.store.get_device(namespace, device_id)

			if device is None:
				raise OwlDeviceNotFoundError(device_id)

			# Delete all entities belonging to this device
			entities = await self.store.get_entities()
			to_delete = [
				(ns, entity_id)
				for (ns, entity_id), ent in entities.items()
				if ent.metadata.get("device_id") == device_id and ent.namespace == namespace
			]

			for ns, entity_id in to_delete:
				await self.entity_manager.remove_entity_from_registries(ns, entity_id)

			# Remove device from HA device registry
			device_registry = dr.async_get(self.manager.hass)
			entry = device_registry.async_get_device(
				identifiers={(DOMAIN, device.unique_id)}
			)

			if entry:
				await device_registry.async_remove_device(entry.id)

			# Remove from store
			self.store.remove_device(device)
			await self.store.save()

			_LOGGER.debug("Deleted device %s", device_id)



	async def cleanup_empty(self, namespace: str) -> None:
		"""Delete devices that no longer have any entities."""
		to_delete = []

		devices = await self.store.get_devices()
		entities = await self.store.get_entities()

		for (ns, device_id), dev in devices.items():
			if ns != namespace:
				continue

			has_entities = any(
				ent.metadata.get("device_id") == device_id and ent.namespace == namespace
				for ent in entities.values()
			)

			if not has_entities:
				to_delete.append(dev)

		for dev in to_delete:
			await self.delete(dev.namespace, dev.device_id)
