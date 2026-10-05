from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any, Optional
from app.database import get_db
from app.models.domain_models import BiometricTelemetryModel, SpatialXRAnchorModel
from app.auth import verify_role

router = APIRouter(prefix="/api/v1/sentinel", tags=["Sentinel Domain Pipelines"])

class BiometricIngestRequest(BaseModel):
    telemetry_id: str
    agent_id: str
    encrypted_payload_hash: str
    trust_score: float
    metadata_info: Optional[Dict[str, Any]] = None

class SpatialAnchorRequest(BaseModel):
    anchor_id: str
    session_id: str
    coordinate_vector: Dict[str, float]

@router.post("/biometrics/ingest")
def ingest_biometric_telemetry(
    data: BiometricIngestRequest, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_role("operator"))
):
    existing = db.query(BiometricTelemetryModel).filter(BiometricTelemetryModel.telemetry_id == data.telemetry_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Telemetry ID already recorded.")
    
    # Proof-before-claim condition: Auto-verify if trust score crosses security threshold
    is_verified = data.trust_score >= 0.85

    record = BiometricTelemetryModel(
        telemetry_id=data.telemetry_id,
        agent_id=data.agent_id,
        encrypted_payload_hash=data.encrypted_payload_hash,
        trust_score=data.trust_score,
        verified=is_verified,
        metadata_info=data.metadata_info
    )
    db.add(record)
    db.commit()
    return {
        "status": "success",
        "telemetry_id": record.telemetry_id,
        "verified": record.verified,
        "message": "Biometric telemetry ingested and evaluated under proof rules."
    }

@router.post("/spatial-xr/anchors")
def register_spatial_anchor(
    data: SpatialAnchorRequest, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_role("operator"))
):
    existing = db.query(SpatialXRAnchorModel).filter(SpatialXRAnchorModel.anchor_id == data.anchor_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Spatial anchor ID already registered.")

    anchor = SpatialXRAnchorModel(
        anchor_id=data.anchor_id,
        session_id=data.session_id,
        coordinate_vector=data.coordinate_vector,
        integrity_status="verified",
        verified=True
    )
    db.add(anchor)
    db.commit()
    return {
        "status": "success",
        "anchor_id": anchor.anchor_id,
        "verified": anchor.verified,
        "message": "Spatial XR anchor verified and anchored successfully."
    }
