# LEGARE123 MISSION OF PROSPERITY
# Starter app for a human-in-the-loop multi-agent evidence orchestration framework.

This repository is a minimal but functional starter for the "Proof Before Claim" approach described in the project concept.

## What this starter includes
- FastAPI application scaffold
- `/api/health` readiness endpoint
- `/api/agents` registry endpoint
- `/api/claims/evaluate` evidence-driven verification endpoint
- basic test suite
- Dockerfile for local containerized execution

## Architecture
The app models the core pattern behind the concept:
- an agent registry where nodes are defined and tracked
- evidence objects that support or refute a claim
- a claim evaluation workflow that checks support before allowing the claim to proceed

## Local development
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Then open:
- http://localhost:8000/
- http://localhost:8000/api/health
- http://localhost:8000/api/agents
- http://localhost:8000/docs

## Example claim evaluation
```bash
curl -X POST http://localhost:8000/api/claims/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "claim": "The system is operating without critical defects.",
    "evidence": [
      "Audit logs confirm no critical defects were observed.",
      "Telemetry shows stable health across the core services."
    ],
    "agent_id": "sentinel-audit"
  }'
```

## Why this matters
This starter turns the concept into a working foundation that can be expanded into:
- a sovereignty and compliance dashboard
- a human-in-the-loop approval workflow
- a multi-agent orchestration engine
- an evidence ledger and claim review system
