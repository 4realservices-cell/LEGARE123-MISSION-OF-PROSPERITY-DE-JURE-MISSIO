from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class AgentStatus(str, Enum):
    REGISTERED = "registered"
    ACTIVE = "active"
    PAUSED = "paused"
    RETIRED = "retired"


class EvidenceStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class ClaimStatus(str, Enum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class UserRole(str, Enum):
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


class AgentRegistration(BaseModel):
    agent_id: str
    name: str
    role: str
    status: AgentStatus = AgentStatus.REGISTERED
    description: Optional[str] = None
    capabilities: List[str] = Field(default_factory=list)

    class Config:
        from_attributes = True


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    status: Optional[AgentStatus] = None
    description: Optional[str] = None
    capabilities: Optional[List[str]] = None


class EvidenceItem(BaseModel):
    evidence_id: str
    source: str
    content: str
    verified: bool = False
    status: EvidenceStatus = EvidenceStatus.PENDING
    submitted_by: Optional[str] = None
    verified_by: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

    class Config:
        from_attributes = True


class EvidenceUpdate(BaseModel):
    source: Optional[str] = None
    content: Optional[str] = None
    status: Optional[EvidenceStatus] = None
    tags: Optional[List[str]] = None


class ClaimEvaluationRequest(BaseModel):
    claim_id: str
    statement: str
    required_evidence_ids: List[str]
    submitted_by: Optional[str] = None


class ClaimEvaluationResponse(BaseModel):
    claim_id: str
    statement: str
    approved: bool
    reason: str
    status: ClaimStatus
    evaluated_at: Optional[datetime] = None
    required_evidence_ids: List[str]


class WorkflowStep(BaseModel):
    step_id: str
    name: str
    description: str
    required_role: str
    order: int


class WorkflowTemplate(BaseModel):
    workflow_id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    created_at: datetime

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    username: str
    password: str
    role: UserRole = UserRole.VIEWER


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    role: UserRole
    is_active: bool = True

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None


class AuditLogEntry(BaseModel):
    id: int
    action: str
    actor: str
    target: Optional[str] = None
    details: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True
