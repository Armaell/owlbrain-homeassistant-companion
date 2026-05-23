from __future__ import annotations

from homeassistant.core import HomeAssistant

from .broadcaster import OwlBrainBroadcaster
from .device_manager import OwlBrainDeviceManager
from .entity_manager import OwlBrainEntityManager

from ..store import OwlBrainStore


class OwlBrainManager:
	"""
	Central orchestrator
	"""

	def __init__(self, hass: HomeAssistant,	store: OwlBrainStore):
		self.hass = hass
		self.store = store

		self.broadcaster = OwlBrainBroadcaster(self)
		self.entities = OwlBrainEntityManager(hass, self, store)
		self.devices = OwlBrainDeviceManager(self, self.entities, store)
