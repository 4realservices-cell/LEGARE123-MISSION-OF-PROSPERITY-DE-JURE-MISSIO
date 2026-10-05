from typing import Dict, List, Optional
from app.models import EvidenceItem

class EvidenceService:
    def __init__(self):
        self._evidence: Dict[str, EvidenceItem] = {}

    def add_evidence(self, item: EvidenceItem) -> EvidenceItem:
        self._evidence[item.evidence_id] = item
        return item

    def get_evidence(self, evidence_id: str) -> Optional[EvidenceItem]:
        return self._evidence.get(evidence_id)

    def verify_evidence(self, evidence_id: str) -> bool:
        item = self._evidence.get(evidence_id)
        if item:
            item.verified = True
            return True
        return False

    def list_evidence(self) -> List[EvidenceItem]:
        return list(self._evidence.values())

evidence_service = EvidenceService()
