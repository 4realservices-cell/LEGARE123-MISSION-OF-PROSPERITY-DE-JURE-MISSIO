from typing import List, Optional
from sqlalchemy.orm import Session
from app.database import ClaimDB, EvidenceDB
from app.models import (
    ClaimEvaluationRequest,
    ClaimEvaluationResponse,
    ClaimStatus,
    EvidenceStatus,
)
from datetime import datetime


class ClaimEvaluationService:
    def __init__(self, db: Session):
        self.db = db

    def evaluate_claim(self, req: ClaimEvaluationRequest, evaluator_id: Optional[str] = None) -> ClaimEvaluationResponse:
        """
        Enforce the proof-before-claim rule:
        1. Check if all required evidence exists
        2. Verify that all required evidence is verified
        3. Only then approve the claim
        """
        # Check if claim already exists
        existing = self.db.query(ClaimDB).filter(ClaimDB.claim_id == req.claim_id).first()
        
        missing_evidence = []
        unverified_evidence = []
        
        for evid_id in req.required_evidence_ids:
            evidence = self.db.query(EvidenceDB).filter(EvidenceDB.evidence_id == evid_id).first()
            if not evidence:
                missing_evidence.append(evid_id)
            elif not evidence.verified or evidence.status != EvidenceStatus.VERIFIED:
                unverified_evidence.append(evid_id)
        
        if missing_evidence:
            reason = f"Claim rejected: Missing evidence: {', '.join(missing_evidence)}"
            status = ClaimStatus.REJECTED
            approved = False
        elif unverified_evidence:
            reason = f"Claim rejected: Unverified evidence: {', '.join(unverified_evidence)}. Proof-before-claim rule enforced."
            status = ClaimStatus.UNDER_REVIEW
            approved = False
        else:
            reason = "Claim approved: All required evidence is present and verified."
            status = ClaimStatus.APPROVED
            approved = True
        
        # Store claim in database
        if existing:
            existing.statement = req.statement
            existing.status = status
            existing.approved = approved
            existing.reason = reason
            existing.evaluated_by = evaluator_id
            existing.evaluated_at = datetime.utcnow()
            self.db.commit()
        else:
            db_claim = ClaimDB(
                claim_id=req.claim_id,
                statement=req.statement,
                status=status,
                approved=approved,
                reason=reason,
                required_evidence_ids=req.required_evidence_ids,
                submitted_by=req.submitted_by,
                evaluated_by=evaluator_id,
                evaluated_at=datetime.utcnow(),
            )
            self.db.add(db_claim)
            self.db.commit()
        
        return ClaimEvaluationResponse(
            claim_id=req.claim_id,
            statement=req.statement,
            approved=approved,
            reason=reason,
            status=status,
            evaluated_at=datetime.utcnow(),
            required_evidence_ids=req.required_evidence_ids,
        )

    def get_claim(self, claim_id: str) -> Optional[dict]:
        db_claim = self.db.query(ClaimDB).filter(ClaimDB.claim_id == claim_id).first()
        if db_claim:
            return {
                "claim_id": db_claim.claim_id,
                "statement": db_claim.statement,
                "status": db_claim.status.value,
                "approved": db_claim.approved,
                "reason": db_claim.reason,
                "required_evidence_ids": db_claim.required_evidence_ids,
                "submitted_by": db_claim.submitted_by,
                "evaluated_by": db_claim.evaluated_by,
                "created_at": db_claim.created_at,
                "evaluated_at": db_claim.evaluated_at,
            }
        return None

    def list_claims(self, status: Optional[ClaimStatus] = None) -> List[dict]:
        query = self.db.query(ClaimDB)
        if status:
            query = query.filter(ClaimDB.status == status)
        
        claims = []
        for db_claim in query.all():
            claims.append({
                "claim_id": db_claim.claim_id,
                "statement": db_claim.statement,
                "status": db_claim.status.value,
                "approved": db_claim.approved,
                "required_evidence_ids": db_claim.required_evidence_ids,
                "created_at": db_claim.created_at,
            })
        return claims

    def archive_claim(self, claim_id: str) -> bool:
        db_claim = self.db.query(ClaimDB).filter(ClaimDB.claim_id == claim_id).first()
        if db_claim:
            db_claim.status = ClaimStatus.ARCHIVED
            self.db.commit()
            return True
        return False
