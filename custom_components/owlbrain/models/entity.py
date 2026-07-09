from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class EntityModel:
	namespace: str
	entity_id: str
	domain: str
	metadata: dict
	unique_id: str
	data: dict[str, Any] = field(default_factory=dict)

	@classmethod
	def from_dict(cls, raw: dict[str, Any]) -> EntityModel:
		return cls(
			namespace=raw.get("namespace", ""),
			entity_id=raw.get("entity_id", ""),
			domain=raw.get("domain", ""),
			metadata=raw.get("metadata", {}) or {},
			unique_id=raw.get("unique_id", ""),
			data=raw.get("data", {}) or {},
		)

	def to_dict(self) -> dict[str, Any]:
		return {
			"namespace": self.namespace,
			"entity_id": self.entity_id,
			"domain": self.domain,
			"metadata": self.metadata,
			"unique_id": self.unique_id,
			"data": self.data,
		}
