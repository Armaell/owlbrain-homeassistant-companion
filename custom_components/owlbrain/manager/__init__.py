from __future__ import annotations

import asyncio

from homeassistant.core import HomeAssistant

from ..store import OwlBrainStore
from .broadcaster import OwlBrainBroadcaster
from .device_manager import OwlBrainDeviceManager
from .entity_manager import OwlBrainEntityManager


class OwlBrainManager:
	"""Central orchestrator."""

	def __init__(self, hass: HomeAssistant, store: OwlBrainStore):
		self.hass = hass
		self.store = store

		# Shared across entities/devices managers so cross-manager operations
		# (device delete touching entities, entity create touching devices)
		# are mutually exclusive.
		lock = asyncio.Lock()

		self.broadcaster = OwlBrainBroadcaster(self)
		self.entities = OwlBrainEntityManager(hass, self, store, lock=lock)
		self.devices = OwlBrainDeviceManager(
			self, self.entities, store, lock=lock
		)
