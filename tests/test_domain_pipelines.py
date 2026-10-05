def test_biometric_telemetry_ingestion_verified(client):
    response = client.post(
        "/api/v1/sentinel/biometrics/ingest",
        json={
            "telemetry_id": "bio-test-001",
            "agent_id": "agent-alpha-1",
            "encrypted_payload_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "trust_score": 0.92,
            "metadata_info": {"device": "biometric-sensor-v2"},
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert data["verified"] is True
    assert data["telemetry_id"] == "bio-test-001"


def test_biometric_telemetry_ingestion_unverified(client):
    response = client.post(
        "/api/v1/sentinel/biometrics/ingest",
        json={
            "telemetry_id": "bio-test-002",
            "agent_id": "agent-beta-2",
            "encrypted_payload_hash": "cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce",
            "trust_score": 0.65,
            "metadata_info": {"device": "legacy-reader"},
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert data["verified"] is False


def test_spatial_xr_anchor_registration(client):
    response = client.post(
        "/api/v1/sentinel/spatial-xr/anchors",
        json={
            "anchor_id": "anchor-philadelphia-hq",
            "session_id": "session-xr-99",
            "coordinate_vector": {"x": 10.5, "y": 45.2, "z": 2.1},
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert data["verified"] is True
    assert data["anchor_id"] == "anchor-philadelphia-hq"
