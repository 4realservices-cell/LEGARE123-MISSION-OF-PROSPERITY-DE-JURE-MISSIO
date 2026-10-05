# Legare123 Mission of Prosperity
# Starter API for a human-in-the-loop evidence governance framework.

This project turns the concept into a runnable FastAPI foundation for the "Proof Before Claim" model.

## What it includes
- an `AgentRegistration` model
- an `EvidenceItem` model
- claim evaluation logic that rejects unverified evidence
- health and readiness endpoints
- a minimal test suite

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Then browse:
- `http://localhost:8000/health`
- `http://localhost:8000/readiness`
- `http://localhost:8000/docs`

## Example claim evaluation
```bash
curl -X POST http://localhost:8000/claims/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "claim_id": "claim-1",
    "statement": "The system is operating under approved conditions.",
    "required_evidence_ids": ["ev-1"]
  }'
```
