from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class DeviceModel:
	namespace: str
	device_id: str
	metadata: dict[str, Any]
	unique_id: str

	@classmethod
	def from_dict(cls, raw: dict[str, Any]) -> DeviceModel:
		return cls(
			namespace=raw.get("namespace", ""),
			device_id=raw.get("device_id", ""),
			metadata=raw.get("metadata", {}) or {},
			unique_id=raw.get("unique_id", ""),
		)

	def to_dict(self) -> dict[str, Any]:
		return {
			"namespace": self.namespace,
			"device_id": self.device_id,
			"metadata": self.metadata,
			"unique_id": self.unique_id,
		}
