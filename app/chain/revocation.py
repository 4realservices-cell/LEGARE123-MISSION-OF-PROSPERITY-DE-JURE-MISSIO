from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, Set


@dataclass
class RevocationRecord:
    template_hash: str
    revoked: bool = False
    reason: str | None = None
    timestamp: str | None = None


class RevocationRegistry:
    """Simple in-memory registry that mirrors the on-chain revocation registry pattern."""

    def __init__(self):
        self._registry: Dict[str, RevocationRecord] = {}

    def revoke(self, template_hash: str, reason: str | None = None, timestamp: str | None = None) -> RevocationRecord:
        record = RevocationRecord(template_hash=template_hash, revoked=True, reason=reason, timestamp=timestamp)
        self._registry[template_hash] = record
        return record

    def check(self, template_hash: str) -> bool:
        record = self._registry.get(template_hash)
        return bool(record and record.revoked)

    def is_revoked(self, template_hash: str) -> bool:
        return self.check(template_hash)

    def remove(self, template_hash: str) -> None:
        self._registry.pop(template_hash, None)
