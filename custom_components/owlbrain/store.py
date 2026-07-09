from __future__ import annotations

import asyncio
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import STORAGE_KEY, STORAGE_VERSION
from .models.device import DeviceModel
from .models.entity import EntityModel

_LOGGER = logging.getLogger(__name__)


class OwlBrainStore:
	"""Persistence layer for OwlBrain with lazy-loaded in-memory cache."""

	def __init__(self, hass: HomeAssistant):
		self.hass = hass
		self._store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
		self._load_lock = asyncio.Lock()

		self._devices: dict[tuple, dict] | None = None
		self._entities: dict[tuple, dict] | None = None

	async def _ensure_loaded(self) -> None:
		if self._devices is not None and self._entities is not None:
			return

		async with self._load_lock:
			if self._devices is not None and self._entities is not None:
				return

			data = await self._store.async_load()

			if not data:
				_LOGGER.debug("No existing OwlBrain storage found")
				self._devices = {}
				self._entities = {}
				return

			self._devices = {
				(dev["namespace"], dev["device_id"]): dev
				for dev in data.get("devices", [])
			}

			self._entities = {
				(ent["namespace"], ent["entity_id"]): ent
				for ent in data.get("entities", [])
			}

	def sync_get_device(
		self, namespace: str, device_id: str
	) -> DeviceModel | None:
		if self._devices is None:
			return None
		raw = self._devices.get((namespace, device_id))
		return DeviceModel.from_dict(raw) if raw else None

	async def get_device(
		self, namespace: str, device_id: str
	) -> DeviceModel | None:
		await self._ensure_loaded()
		raw = self._devices.get((namespace, device_id))
		return DeviceModel.from_dict(raw) if raw else None

	async def get_devices(self, namespace=None) -> dict[tuple, DeviceModel]:
		await self._ensure_loaded()
		return {
			key: DeviceModel.from_dict(raw)
			for key, raw in self._devices.items()
			if namespace is None or key[0] == namespace
		}

	async def get_entity(
		self, namespace: str, entity_id: str
	) -> EntityModel | None:
		await self._ensure_loaded()
		raw = self._entities.get((namespace, entity_id))
		return EntityModel.from_dict(raw) if raw else None

	async def get_entities(self, namespace=None) -> dict[tuple, EntityModel]:
		await self._ensure_loaded()
		return {
			key: EntityModel.from_dict(raw)
			for key, raw in self._entities.items()
			if namespace is None or key[0] == namespace
		}

	async def save(self) -> None:
		await self._ensure_loaded()
		data = {
			"devices": list(self._devices.values()),
			"entities": list(self._entities.values()),
		}
		await self._store.async_save(data)

	async def set_device(self, model: DeviceModel) -> None:
		await self._ensure_loaded()
		self._devices[(model.namespace, model.device_id)] = model.to_dict()

	async def set_entity(self, model: EntityModel) -> None:
		await self._ensure_loaded()
		self._entities[(model.namespace, model.entity_id)] = model.to_dict()

	async def save_device(self, model: DeviceModel) -> None:
		await self.set_device(model)
		await self.save()

	async def save_entity(self, model: EntityModel) -> None:
		await self.set_entity(model)
		await self.save()

	def remove_device(self, model: DeviceModel) -> None:
		self._devices.pop((model.namespace, model.device_id), None)

	def remove_entity(self, model: EntityModel) -> None:
		self._entities.pop((model.namespace, model.entity_id), None)
