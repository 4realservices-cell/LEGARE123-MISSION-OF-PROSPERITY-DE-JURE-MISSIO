from fastapi import FastAPI, HTTPException
from app.config import settings
from app.models import (
    AgentRegistration,
    EvidenceItem,
    ClaimEvaluationRequest,
    ClaimEvaluationResponse
)
from app.services.agent_registry import agent_registry
from app.services.evidence_service import evidence_service

app = FastAPI(title=settings.app_name)

@app.get("/health")
def health_check():
    return {"status": "healthy", "environment": settings.environment}

@app.get("/readiness")
def readiness_check():
    return {"status": "ready"}

@app.post("/agents", response_model=AgentRegistration)
def register_agent(agent: AgentRegistration):
    return agent_registry.register_agent(agent)

@app.get("/agents", response_model=list[AgentRegistration])
def list_agents():
    return agent_registry.list_agents()

@app.post("/evidence", response_model=EvidenceItem)
def add_evidence(item: EvidenceItem):
    return evidence_service.add_evidence(item)

@app.get("/evidence", response_model=list[EvidenceItem])
def list_evidence():
    return evidence_service.list_evidence()

@app.post("/claims/evaluate", response_model=ClaimEvaluationResponse)
def evaluate_claim(req: ClaimEvaluationRequest):
    for evid_id in req.required_evidence_ids:
        item = evidence_service.get_evidence(evid_id)
        if not item:
            raise HTTPException(
                status_code=400,
                detail=f"Evidence ID '{evid_id}' not found."
            )
        if not item.verified:
            return ClaimEvaluationResponse(
                claim_id=req.claim_id,
                statement=req.statement,
                approved=False,
                reason=f"Claim rejected: Evidence '{evid_id}' is unverified. Proof-before-claim rule enforced."
            )

    return ClaimEvaluationResponse(
        claim_id=req.claim_id,
        statement=req.statement,
        approved=True,
        reason="Claim approved: All required evidence is present and verified."
    )
