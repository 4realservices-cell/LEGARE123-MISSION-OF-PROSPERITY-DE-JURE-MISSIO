from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "LEGARE123 Mission of Prosperity"
    assert payload["principle"] == "Proof Before Claim"


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_agent_registry():
    response = client.get("/api/agents")
    assert response.status_code == 200
    data = response.json()["agents"]
    assert len(data) >= 2
    assert data[0]["id"] == "sentinel-audit"


def test_valid_claim_verification():
    payload = {
        "claim": "The system is operating without critical defects.",
        "evidence": [
            "The system is operating without critical defects, as confirmed by audit logs and telemetry checks.",
            "No critical alerts were detected.",
        ],
        "agent_id": "sentinel-audit",
    }
    response = client.post("/api/claims/evaluate", json=payload)
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "verified"
    assert result["proof_before_claim"] is True


def test_invalid_claim_rejection():
    payload = {
        "claim": "The system is secure.",
        "evidence": ["A deployment was scheduled, but no audit data is attached."],
    }
    response = client.post("/api/claims/evaluate", json=payload)
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "rejected"
