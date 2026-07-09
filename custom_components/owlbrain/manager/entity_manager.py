from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity import Entity

from ..domain import DOMAIN_HANDLERS
from ..errors import (
	OwlDeviceNotFoundError,
	OwlEntityNotFoundError,
	OwlNamespaceCollisionError,
	OwlPlatformNotReadyError,
	OwlUnsupportedDomainError,
)
from ..models.entity import EntityModel
from ..store import OwlBrainStore
from ..utils.ids import build_unique_id_entity

_LOGGER = logging.getLogger(__name__)


class OwlBrainEntityManager:
	def __init__(
		self,
		hass: HomeAssistant,
		manager,
		store: OwlBrainStore,
		lock: asyncio.Lock | None = None,
	):
		self._lock = lock or asyncio.Lock()
		self.hass = hass
		self.manager = manager
		self.store = store

		# Runtime HA entities (unique_id, entity instance)
		self.runtime_entities: dict[str, Any] = {}

		# Platform adders (domain, platform.async_add_entities) — the real
		# EntityPlatform coroutine, which only resolves once entities are
		# fully added to hass (not the fire-and-forget AddEntitiesCallback).
		self.platform_adders: dict[
			str, Callable[[list[Entity]], Awaitable[None]]
		] = {}

	def register_platform(
		self, domain: str, adder: Callable[[list[Entity]], Awaitable[None]]
	):
		"""Called by each platform file (sensor.py, switch.py, etc.)."""
		self.platform_adders[domain] = adder

	async def restore_runtime_entities(self) -> None:
		"""Recreate all runtime entities from persisted storage."""
		entities = await self.store.get_entities()
		restored = 0
		async with self._lock:
			for entity in entities.values():
				try:
					await self._create_runtime_entity(entity)
					restored += 1
				except Exception as err:
					_LOGGER.error(
						"Failed to restore entity %s (domain %s): %s",
						entity.entity_id,
						entity.domain,
						err,
					)

		_LOGGER.info(
			"OwlBrain restored %s/%s entities", restored, len(entities)
		)

	async def create(
		self, namespace: str, entity_id: str, metadata: dict
	) -> EntityModel:
		async with self._lock:
			return await self._create_locked(namespace, entity_id, metadata)

	async def _create_locked(
		self, namespace: str, entity_id: str, metadata: dict
	) -> EntityModel:
		domain = entity_id.split(".")[0]
		entity_cls = DOMAIN_HANDLERS.get(domain)
		if entity_cls is None:
			raise OwlUnsupportedDomainError(domain)

		# Namespace collision check
		entities = await self.store.get_entities()
		for ns, eid in entities:
			if eid == entity_id and ns != namespace:
				raise OwlNamespaceCollisionError(entity_id, ns)

		device_id = metadata.get("device_id")
		if device_id:
			device = await self.store.get_device(namespace, device_id)
			if device is None:
				raise OwlDeviceNotFoundError(device_id)

		validated_metadata = entity_cls.validate_metadata(metadata)

		# Build model
		model = EntityModel(
			namespace=namespace,
			entity_id=entity_id,
			domain=domain,
			unique_id=build_unique_id_entity(namespace, entity_id),
			data={},
			metadata=validated_metadata,
		)

		if device_id:
			model.device_id = device_id

		await self.store.set_entity(model)
		try:
			await self._create_runtime_entity(model)
		except Exception:
			self.store.remove_entity(model)
			raise
		await self.manager.devices._cleanup_empty_locked(namespace)
		await self.store.save()

		_LOGGER.info(f"created entity {entity_id}")
		return model

	async def update_metadata(
		self, namespace: str, entity_id: str, metadata: dict
	):
		async with self._lock:
			return await self._update_metadata_locked(
				namespace, entity_id, metadata
			)

	async def _update_metadata_locked(
		self, namespace: str, entity_id: str, metadata: dict
	):
		entity = await self.store.get_entity(namespace, entity_id)

		if entity is None:
			raise OwlEntityNotFoundError(entity_id)

		device_id = metadata.get("device_id")
		if device_id:
			device = await self.store.get_device(namespace, device_id)
			if device is None:
				raise OwlDeviceNotFoundError(device_id)

		entity_cls = DOMAIN_HANDLERS.get(entity.domain)
		validated_metadata = (
			entity_cls.validate_metadata(metadata)
			if entity_cls
			else dict(metadata)
		)

		entity.metadata = validated_metadata
		entity.device_id = device_id if device_id else None

		await self.store.save_entity(entity)

		runtime = self.runtime_entities.get(entity.unique_id)
		if runtime:
			await runtime.async_update_metadata(validated_metadata)

		_LOGGER.debug(f"updated entity {entity_id}'s metadata with {metadata}")
		return entity

	async def upsert(
		self, namespace: str, entity_id: str, metadata: dict
	) -> tuple[EntityModel, str]:
		"""Create the entity if it doesn't exist yet, else update its metadata.

		Runs the existence check and the create/update under a single lock
		acquisition so a concurrent delete can't land between the check and
		the write.
		"""
		async with self._lock:
			entity = await self.store.get_entity(namespace, entity_id)
			if entity is None:
				return (
					await self._create_locked(namespace, entity_id, metadata),
					"created",
				)
			return (
				await self._update_metadata_locked(
					namespace, entity_id, metadata
				),
				"updated",
			)

	async def update_data(
		self, namespace: str, entity_id: str, data: dict
	) -> EntityModel:
		async with self._lock:
			entity = await self.store.get_entity(namespace, entity_id)

			if entity is None:
				raise OwlEntityNotFoundError(entity_id)

			runtime = self.runtime_entities.get(entity.unique_id)
			if runtime is None:
				raise OwlPlatformNotReadyError(entity.domain)

			data = await runtime.async_update_data(data)
			entity.data = data
			await self.store.save_entity(entity)

			return entity

	async def delete(self, namespace: str, entity_id: str):
		async with self._lock:
			await self._remove_entity_from_registries_locked(
				namespace, entity_id
			)
			await self.manager.devices._cleanup_empty_locked(namespace)
			await self.store.save()
			_LOGGER.debug("Deleted entity %s", entity_id)

	async def _create_runtime_entity(self, model: EntityModel):
		"""Create a HA entity instance and inject it into the platform."""
		domain = model.domain
		entity_cls = DOMAIN_HANDLERS.get(domain)
		if not entity_cls:
			raise OwlUnsupportedDomainError(domain)

		if domain not in self.platform_adders:
			raise OwlPlatformNotReadyError(domain)

		entity = entity_cls(self.hass, self.manager, model)

		# Await full HA registration before considering the entity live, so
		# no update/refresh can ever observe it half-added.
		await self.platform_adders[domain]([entity])
		self.runtime_entities[model.unique_id] = entity

	async def remove_entity_from_registries(
		self, namespace: str, entity_id: str
	):
		"""Remove entity from internal and HA registries."""
		async with self._lock:
			await self._remove_entity_from_registries_locked(
				namespace, entity_id
			)

	async def _remove_entity_from_registries_locked(
		self, namespace: str, entity_id: str
	):
		entity = await self.store.get_entity(namespace, entity_id)

		if entity is None:
			raise OwlEntityNotFoundError(entity_id)

		unique_id = entity.unique_id

		entity_registry = er.async_get(self.hass)
		entry = entity_registry.async_get_entity_id(
			entity.domain, "owlbrain", unique_id
		)

		if entry:
			entity_registry.async_remove(entry)

		runtime = self.runtime_entities.pop(unique_id, None)
		if runtime:
			await runtime.async_remove()

		self.store.remove_entity(entity)

	def force_ha_refresh(self, namespace: str):
		# force refresh all ha entities in this namespace
		for entity in self.runtime_entities.values():
			if entity.owl_namespace == namespace:
				entity.async_write_ha_state()
