from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal

client = TestClient(app)
db = SessionLocal()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_readiness():
    response = client.get("/readiness")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_list_agents():
    response = client.get("/api/v1/agents")
    assert response.status_code == 200
    agents = response.json()
    assert len(agents) >= 3  # We seed 3 agents
    assert any(a["agent_id"] == "sentinel-audit" for a in agents)


def test_list_evidence():
    response = client.get("/api/v1/evidence")
    assert response.status_code == 200
    evidence = response.json()
    assert len(evidence) >= 3  # We seed 3 evidence items


def test_proof_before_claim_rejection():
    """Test that unverified evidence causes claim rejection."""
    response = client.post("/api/v1/claims/evaluate", json={
        "claim_id": "test-claim-reject-001",
        "statement": "This system is secure.",
        "required_evidence_ids": ["ev-security-scan-001"],  # Unverified evidence
        "submitted_by": "test-user",
    })
    assert response.status_code == 200
    result = response.json()
    assert result["approved"] is False
    assert "unverified" in result["reason"].lower()


def test_proof_before_claim_approval():
    """Test that verified evidence causes claim approval."""
    response = client.post("/api/v1/claims/evaluate", json={
        "claim_id": "test-claim-approve-001",
        "statement": "System audit shows no critical defects.",
        "required_evidence_ids": ["ev-system-audit-001"],  # Verified evidence
        "submitted_by": "test-user",
    })
    assert response.status_code == 200
    result = response.json()
    assert result["approved"] is True
    assert "approved" in result["reason"].lower()


def test_missing_evidence():
    """Test that missing evidence causes claim rejection."""
    response = client.post("/api/v1/claims/evaluate", json={
        "claim_id": "test-claim-missing-001",
        "statement": "This is a test claim.",
        "required_evidence_ids": ["ev-nonexistent-001"],  # Doesn't exist
        "submitted_by": "test-user",
    })
    assert response.status_code == 200
    result = response.json()
    assert result["approved"] is False
    assert "missing" in result["reason"].lower()


def test_list_workflows():
    response = client.get("/api/v1/workflows")
    assert response.status_code == 200
    workflows = response.json()
    assert len(workflows) >= 2  # We seed 2 workflows
    assert any(w["workflow_id"] == "wf-claim-approval" for w in workflows)


def test_admin_dashboard():
    response = client.get("/admin")
    assert response.status_code == 200
    assert "LEGARE123" in response.text
    assert "Admin Dashboard" in response.text
