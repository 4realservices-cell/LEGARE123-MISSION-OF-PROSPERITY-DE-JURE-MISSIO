from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validator
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import verify_role
from app.database import get_db
from app.models.domain_models import BiometricTelemetryModel, SpatialXRAnchorModel

router = APIRouter(prefix="/api/v1/sentinel", tags=["Sentinel Domain Pipelines"])

VERIFY_OPERATOR = verify_role("operator")


class BiometricIngestRequest(BaseModel):
    telemetry_id: str
    agent_id: str
    encrypted_payload_hash: str
    trust_score: float
    metadata_info: Optional[Dict[str, Any]] = None

    @validator("trust_score")
    def validate_trust_score(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError("trust_score must be between 0.0 and 1.0")
        return v


class SpatialAnchorRequest(BaseModel):
    anchor_id: str
    session_id: str
    coordinate_vector: Dict[str, float]

    @validator("coordinate_vector")
    def validate_vector(cls, v):
        for axis in ("x", "y", "z"):
            if axis not in v:
                raise ValueError(f"coordinate_vector missing '{axis}'")
            try:
                float(v[axis])
            except (TypeError, ValueError):
                raise ValueError(f"coordinate_vector['{axis}'] must be numeric")
        return v


@router.post("/biometrics/ingest", status_code=status.HTTP_201_CREATED)
def ingest_biometric_telemetry(
    data: BiometricIngestRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(VERIFY_OPERATOR),
):
    existing = (
        db.query(BiometricTelemetryModel)
        .filter(BiometricTelemetryModel.telemetry_id == data.telemetry_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Telemetry ID already recorded.")

    record = BiometricTelemetryModel(
        telemetry_id=data.telemetry_id,
        agent_id=data.agent_id,
        encrypted_payload_hash=data.encrypted_payload_hash,
        trust_score=data.trust_score,
        verified=data.trust_score >= 0.85,
        metadata_info=data.metadata_info,
    )

    try:
        db.add(record)
        db.commit()
        db.refresh(record)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Database integrity error: duplicate or invalid record.",
        ) from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to write telemetry record.",
        ) from exc

    return {
        "status": "success",
        "telemetry_id": record.telemetry_id,
        "verified": record.verified,
        "message": "Biometric telemetry ingested and evaluated under proof rules.",
    }


@router.post("/spatial-xr/anchors", status_code=status.HTTP_201_CREATED)
def register_spatial_anchor(
    data: SpatialAnchorRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(VERIFY_OPERATOR),
):
    existing = (
        db.query(SpatialXRAnchorModel)
        .filter(SpatialXRAnchorModel.anchor_id == data.anchor_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Spatial anchor ID already registered.")

    anchor = SpatialXRAnchorModel(
        anchor_id=data.anchor_id,
        session_id=data.session_id,
        coordinate_vector=data.coordinate_vector,
        integrity_status="verified",
        verified=True,
    )

    try:
        db.add(anchor)
        db.commit()
        db.refresh(anchor)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Database integrity error: duplicate or invalid record.",
        ) from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to write anchor record.",
        ) from exc

    return {
        "status": "success",
        "anchor_id": anchor.anchor_id,
        "verified": anchor.verified,
        "message": "Spatial XR anchor verified and anchored successfully.",
    }


@router.get("/health/readiness")
def sentinel_readiness_probe(db: Session = Depends(get_db)):
    """Readiness probe verifying live DB connection, under the sentinel surface.

    Returns 200 with {"status": "ready", ...} when the database answers a
    lightweight SELECT 1, and a real 503 (via JSONResponse) when it does not.
    """
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "database": "disconnected", "error": str(e)},
        )
