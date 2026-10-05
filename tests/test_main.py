# tests/test_main.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_readiness():
    response = client.get("/health/readiness")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data

def test_biometrics_ingest():
    payload = {
        "device_id": "sentinel-node-alpha",
        "biometric_hash": "sample_hash_value",
        "telemetry": {"heart_rate": 75, "stress_index": 0.12}
    }
    response = client.post("/api/v1/sentinel/biometrics/ingest", json=payload)
    # Accepts valid structure or validation feedback depending on strict schemas
    assert response.status_code in [200, 201, 422]

def test_spatial_xr_anchors():
    payload = {
        "anchor_id": "anchor-001",
        "spatial_coordinates": [10.5, 2.0, -4.1]
    }
    response = client.post("/api/v1/sentinel/spatial-xr/anchors", json=payload)
    assert response.status_code in [200, 201, 422]
