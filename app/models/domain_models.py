from sqlalchemy import Column, String, Boolean, Float, DateTime, JSON
from datetime import datetime
from app.database import Base


class BiometricTelemetryModel(Base):
    __tablename__ = "biometric_telemetry"

    telemetry_id = Column(String, primary_key=True, index=True)
    agent_id = Column(String, index=True, nullable=False)
    encrypted_payload_hash = Column(String, nullable=False)
    trust_score = Column(Float, default=0.0)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata_info = Column(JSON, nullable=True)


class SpatialXRAnchorModel(Base):
    __tablename__ = "spatial_xr_anchors"

    anchor_id = Column(String, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False)
    coordinate_vector = Column(JSON, nullable=False)  # e.g. {"x": 0.0, "y": 0.0, "z": 0.0}
    integrity_status = Column(String, default="unverified")  # unverified, verified, revoked
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
