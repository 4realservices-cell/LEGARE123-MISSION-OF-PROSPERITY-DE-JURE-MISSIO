"""Strict tests for the payloads provided 2026-10-05 and the sentinel readiness route.

Unlike tests/test_main.py, these do NOT accept 422 as a passing outcome:
each test proves the contract it names, or it fails.
"""

import pytest
from pydantic import ValidationError

from app.models.schemas import BiometricIngestPayload, SpatialXREnterAnchor


# --- Schema tests (pure, no app boot) ---


def test_spatial_anchor_accepts_exactly_three_coordinates():
    anchor = SpatialXREnterAnchor(anchor_id="anchor-001", spatial_coordinates=[10.5, 2.0, -4.1])
    assert anchor.to_coordinate_vector() == {"x": 10.5, "y": 2.0, "z": -4.1}


@pytest.mark.parametrize("coords", [[1.0, 2.0], [1.0, 2.0, 3.0, 4.0], []])
def test_spatial_anchor_rejects_non_three_coordinates(coords):
    with pytest.raises(ValidationError):
        SpatialXREnterAnchor(anchor_id="anchor-x", spatial_coordinates=coords)


def test_biometric_payload_accepts_iso8601_timestamp():
    payload = BiometricIngestPayload(
        device_id="sentinel-node-alpha",
        timestamp="2026-10-05T20:08:58-04:00",
        metrics={"heart_rate": 75, "galvanic_skin_response": 0.42},
    )
    assert payload.device_id == "sentinel-node-alpha"
    assert payload.metadata is None


def test_biometric_payload_rejects_non_iso8601_timestamp():
    with pytest.raises(ValidationError):
        BiometricIngestPayload(
            device_id="sentinel-node-alpha",
            timestamp="not-a-timestamp",
            metrics={"heart_rate": 75},
        )


# --- Readiness tests (client/app fixtures from tests/conftest.py) ---


def test_sentinel_readiness_ready(client):
    response = client.get("/api/v1/sentinel/health/readiness")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_sentinel_readiness_returns_503_when_db_fails(client, app):
    from app.database import get_db

    def failing_db():
        class _Boom:
            def execute(self, *args, **kwargs):
                raise RuntimeError("db down")

        yield _Boom()

    previous = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = failing_db
    try:
        response = client.get("/api/v1/sentinel/health/readiness")
    finally:
        if previous is not None:
            app.dependency_overrides[get_db] = previous
        else:
            app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 503
    assert response.json()["status"] == "unhealthy"


def test_legacy_readiness_returns_503_when_db_fails(client, app):
    """The pre-existing /health/readiness route previously returned a
    (dict, 503) tuple, which never delivered a real 503. Prove the fix."""
    from app.database import get_db

    def failing_db():
        class _Boom:
            def execute(self, *args, **kwargs):
                raise RuntimeError("db down")

        yield _Boom()

    previous = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = failing_db
    try:
        response = client.get("/health/readiness")
    finally:
        if previous is not None:
            app.dependency_overrides[get_db] = previous
        else:
            app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 503
    assert response.json()["status"] == "unhealthy"
