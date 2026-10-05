from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_proof_before_claim_rule():
    client.post("/evidence", json={
        "evidence_id": "ev-1",
        "source": "test-source",
        "content": "test data",
        "verified": False
    })

    response = client.post("/claims/evaluate", json={
        "claim_id": "claim-1",
        "statement": "Test statement",
        "required_evidence_ids": ["ev-1"]
    })
    assert response.status_code == 200
    assert response.json()["approved"] is False

    client.post("/evidence", json={
        "evidence_id": "ev-2",
        "source": "test-source-2",
        "content": "verified data",
        "verified": True
    })

    response_pass = client.post("/claims/evaluate", json={
        "claim_id": "claim-2",
        "statement": "Valid statement",
        "required_evidence_ids": ["ev-2"]
    })
    assert response_pass.status_code == 200
    assert response_pass.json()["approved"] is True
