from typing import List, Optional
from sqlalchemy.orm import Session
from app.database import EvidenceDB
from app.models import EvidenceItem, EvidenceStatus, EvidenceUpdate
from datetime import datetime


class EvidenceService:
    def __init__(self, db: Session):
        self.db = db

    def add_evidence(self, item: EvidenceItem) -> EvidenceItem:
        db_evidence = EvidenceDB(
            evidence_id=item.evidence_id,
            source=item.source,
            content=item.content,
            verified=item.verified,
            status=item.status,
            submitted_by=item.submitted_by,
            tags=item.tags,
        )
        self.db.add(db_evidence)
        self.db.commit()
        self.db.refresh(db_evidence)
        return EvidenceItem.from_orm(db_evidence)

    def get_evidence(self, evidence_id: str) -> Optional[EvidenceItem]:
        db_evidence = self.db.query(EvidenceDB).filter(EvidenceDB.evidence_id == evidence_id).first()
        return EvidenceItem.from_orm(db_evidence) if db_evidence else None

    def list_evidence(self, status: Optional[EvidenceStatus] = None, tags: Optional[List[str]] = None) -> List[EvidenceItem]:
        query = self.db.query(EvidenceDB)
        if status:
            query = query.filter(EvidenceDB.status == status)
        results = query.all()
        
        if tags:
            results = [e for e in results if any(tag in e.tags for tag in tags)]
        
        return [EvidenceItem.from_orm(evidence) for evidence in results]

    def verify_evidence(self, evidence_id: str, verified_by: str) -> bool:
        db_evidence = self.db.query(EvidenceDB).filter(EvidenceDB.evidence_id == evidence_id).first()
        if db_evidence:
            db_evidence.verified = True
            db_evidence.status = EvidenceStatus.VERIFIED
            db_evidence.verified_by = verified_by
            db_evidence.updated_at = datetime.utcnow()
            self.db.commit()
            return True
        return False

    def reject_evidence(self, evidence_id: str) -> bool:
        db_evidence = self.db.query(EvidenceDB).filter(EvidenceDB.evidence_id == evidence_id).first()
        if db_evidence:
            db_evidence.verified = False
            db_evidence.status = EvidenceStatus.REJECTED
            db_evidence.updated_at = datetime.utcnow()
            self.db.commit()
            return True
        return False

    def update_evidence(self, evidence_id: str, update: EvidenceUpdate) -> Optional[EvidenceItem]:
        db_evidence = self.db.query(EvidenceDB).filter(EvidenceDB.evidence_id == evidence_id).first()
        if not db_evidence:
            return None
        
        update_data = update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_evidence, key, value)
        
        db_evidence.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_evidence)
        return EvidenceItem.from_orm(db_evidence)

    def delete_evidence(self, evidence_id: str) -> bool:
        db_evidence = self.db.query(EvidenceDB).filter(EvidenceDB.evidence_id == evidence_id).first()
        if db_evidence:
            self.db.delete(db_evidence)
            self.db.commit()
            return True
        return False
