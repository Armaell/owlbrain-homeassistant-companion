from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class EntityModel:
    namespace: str
    entity_id: str
    domain: str
    metadata: Dict
    unique_id: str
    data: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, raw: Dict[str, Any]) -> "EntityModel":
        return cls(
            namespace=raw.get("namespace", ""),
            entity_id=raw.get("entity_id", ""),
            domain=raw.get("domain", ""),
            metadata=raw.get("metadata", {}) or {},
            unique_id=raw.get("unique_id", ""),
            data=raw.get("data", {}) or {}
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespace": self.namespace,
            "entity_id": self.entity_id,
            "domain": self.domain,
            "metadata": self.metadata,
            "unique_id": self.unique_id,
            "data": self.data
        }
