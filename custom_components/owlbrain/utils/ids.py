from __future__ import annotations

from ..const import UNIQUE_ID_DEVICE, UNIQUE_ID_ENTITY


def build_unique_id_device(namespace: str, device_id: str) -> str:
	return UNIQUE_ID_DEVICE.format(namespace=namespace, device_id=device_id)


def build_unique_id_entity(namespace: str, entity_id: str) -> str:
	return UNIQUE_ID_ENTITY.format(namespace=namespace, entity_id=entity_id)
