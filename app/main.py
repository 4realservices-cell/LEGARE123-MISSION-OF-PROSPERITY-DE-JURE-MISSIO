from typing import Optional

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.config import settings
from app.services.agent_registry import list_agents
from app.services.evidence_service import evaluate_claim

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Starter framework for a human-in-the-loop multi-agent evidence orchestration system. "
        "The design principle is 'Proof Before Claim.'"
    ),
)


@app.get("/")
async def root() -> dict:
    return {
        "name": settings.app_name,
        "status": "running",
        "version": settings.app_version,
        "principle": "Proof Before Claim",
        "environment": settings.app_env,
    }


@app.get(f"{settings.api_prefix}/health")
async def health() -> dict:
    return {"status": "ok", "service": settings.app_name}


@app.get(f"{settings.api_prefix}/agents")
async def agents() -> dict:
    return {"agents": list_agents()}


@app.post(f"{settings.api_prefix}/claims/evaluate")
async def evaluate_claim_endpoint(payload: dict) -> dict:
    claim = payload.get("claim", "")
    evidence = payload.get("evidence", [])
    agent_id = payload.get("agent_id")

    if not isinstance(evidence, list):
        return JSONResponse(
            status_code=400,
            content={"detail": "The 'evidence' field must be a list of strings."},
        )

    if not claim.strip():
        return JSONResponse(
            status_code=400,
            content={"detail": "The 'claim' field cannot be empty."},
        )

    result = evaluate_claim(
        claim=claim,
        evidence=evidence,
        agent_id=agent_id,
    )
    return result
