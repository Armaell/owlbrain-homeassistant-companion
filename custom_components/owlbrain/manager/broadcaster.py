from __future__ import annotations

import logging
from typing import Any

from ..const import WS_MESSAGE_VERSION

logger = logging.getLogger(__name__)


class OwlBrainBroadcaster:
	"""Manage WebSocket subscribers and broadcast events to them."""

	def __init__(self, manager):
		self._manager = manager
		self._subs: dict[str, set] = {}

	def add(self, namespace: str, connection):
		"""Add a client to which send `owlbrain_entity_action` messages."""
		self._subs.setdefault(namespace, set()).add(connection)
		self._manager.entities.force_ha_refresh(namespace)

	def remove(self, namespace: str, connection):
		if namespace in self._subs:
			self._subs[namespace].discard(connection)

			if not self._subs[namespace]:
				del self._subs[namespace]
				self._manager.entities.force_ha_refresh(namespace)

	def available(self, namespace: str) -> bool:
		"""Check if an active connection exists for the namespace."""
		return bool(self._subs.get(namespace))

	def broadcast(self, namespace: str, message: dict):
		"""Broadcast a message to all subscribers of a namespace."""
		subs = self._subs.get(namespace, set())

		for conn in list(subs):
			try:
				conn.send_message(message)
			except Exception:
				logger.exception(
					"Failed to send message to a subscriber of namespace %s",
					namespace,
				)
				subs.discard(conn)

	async def broadcast_entity_action(
		self, namespace: str, entity_id: str, action: str, data: dict[str, Any]
	):
		"""Broadcast an `owlbrain_entity_action` to namespace subscribers."""
		message = {
			"type": "owlbrain_entity_action",
			"version": WS_MESSAGE_VERSION,
			"namespace": namespace,
			"entity_id": entity_id,
			"action": action,
			"data": data,
		}
		self.broadcast(namespace, message)
