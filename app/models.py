from pydantic import BaseModel, Field
from typing import List, Optional


class AgentRecord(BaseModel):
    id: str
    name: str
    role: str
    status: str = "active"
    description: str


class ClaimSubmission(BaseModel):
    claim: str = Field(..., min_length=1)
    evidence: List[str] = Field(default_factory=list)
    agent_id: Optional[str] = None

    class Config:
        orm_mode = True
