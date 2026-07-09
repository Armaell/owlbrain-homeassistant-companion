from __future__ import annotations

import asyncio
import logging

from homeassistant.helpers import device_registry as dr

from ..const import DOMAIN
from ..errors import OwlDeviceNotFoundError, OwlNamespaceCollisionError
from ..models.device import DeviceModel
from ..store import OwlBrainStore
from ..utils.ids import build_unique_id_device
from .entity_manager import OwlBrainEntityManager

_LOGGER = logging.getLogger(__name__)


class OwlBrainDeviceManager:
	def __init__(
		self,
		manager,
		entity_manager: OwlBrainEntityManager,
		store: OwlBrainStore,
		lock: asyncio.Lock | None = None,
	):
		self._lock = lock or asyncio.Lock()
		self.manager = manager
		self.entity_manager = entity_manager
		self.store = store

	async def create(
		self, namespace: str, device_id: str, metadata: dict
	) -> DeviceModel:
		"""Create a device."""
		async with self._lock:
			return await self._create_locked(namespace, device_id, metadata)

	async def _create_locked(
		self, namespace: str, device_id: str, metadata: dict
	) -> DeviceModel:
		devices = await self.store.get_devices()

		# Check for namespace collision
		for ns, did in devices:
			if did == device_id and ns != namespace:
				raise OwlNamespaceCollisionError(device_id, ns)

		device = DeviceModel(
			namespace=namespace,
			device_id=device_id,
			metadata=metadata,
			unique_id=build_unique_id_device(namespace, device_id),
		)

		await self.store.save_device(device)
		_LOGGER.info("Created device %s", device_id)
		return device

	async def update(
		self, namespace: str, device_id: str, metadata: dict
	) -> DeviceModel:
		"""Update a device by overwriting its metadata."""
		async with self._lock:
			return await self._update_locked(namespace, device_id, metadata)

	async def _update_locked(
		self, namespace: str, device_id: str, metadata: dict
	) -> DeviceModel:
		device = await self.store.get_device(namespace, device_id)

		if device is None:
			raise OwlDeviceNotFoundError(device_id)

		device.metadata = metadata

		await self.store.save_device(device)
		_LOGGER.debug("Updated device %s's metadata", device_id)
		return device

	async def upsert(
		self, namespace: str, device_id: str, metadata: dict
	) -> tuple[DeviceModel, str]:
		"""Create the device if it doesn't exist yet, else update it.

		Runs the existence check and the create/update under a single lock
		acquisition so a concurrent delete can't land between the check and
		the write.
		"""
		async with self._lock:
			device = await self.store.get_device(namespace, device_id)
			if device is None:
				return (
					await self._create_locked(namespace, device_id, metadata),
					"created",
				)
			return (
				await self._update_locked(namespace, device_id, metadata),
				"updated",
			)

	async def delete(self, namespace: str, device_id: str) -> None:
		async with self._lock:
			await self._delete_locked(namespace, device_id)

	async def _delete_locked(self, namespace: str, device_id: str) -> None:
		device = await self.store.get_device(namespace, device_id)

		if device is None:
			raise OwlDeviceNotFoundError(device_id)

		# Delete all entities belonging to this device
		entities = await self.store.get_entities()
		to_delete = [
			(ns, entity_id)
			for (ns, entity_id), ent in entities.items()
			if ent.metadata.get("device_id") == device_id
			and ent.namespace == namespace
		]

		for ns, entity_id in to_delete:
			await self.entity_manager._remove_entity_from_registries_locked(
				ns, entity_id
			)

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
		async with self._lock:
			await self._cleanup_empty_locked(namespace)

	async def _cleanup_empty_locked(self, namespace: str) -> None:
		to_delete = []

		devices = await self.store.get_devices()
		entities = await self.store.get_entities()

		for (ns, device_id), dev in devices.items():
			if ns != namespace:
				continue

			has_entities = any(
				ent.metadata.get("device_id") == device_id
				and ent.namespace == namespace
				for ent in entities.values()
			)

			if not has_entities:
				to_delete.append(dev)

		for dev in to_delete:
			await self._delete_locked(dev.namespace, dev.device_id)
