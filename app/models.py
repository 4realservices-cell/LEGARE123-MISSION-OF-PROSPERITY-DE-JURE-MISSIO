from pydantic import BaseModel
from typing import List

class AgentRegistration(BaseModel):
    agent_id: str
    name: str
    role: str
    status: str = "active"

class EvidenceItem(BaseModel):
    evidence_id: str
    source: str
    content: str
    verified: bool = False

class ClaimEvaluationRequest(BaseModel):
    claim_id: str
    statement: str
    required_evidence_ids: List[str]

class ClaimEvaluationResponse(BaseModel):
    claim_id: str
    statement: str
    approved: bool
    reason: str
