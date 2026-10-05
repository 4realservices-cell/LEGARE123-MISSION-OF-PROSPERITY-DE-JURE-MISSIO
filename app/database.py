from sqlalchemy import create_engine, Column, String, Boolean, DateTime, JSON, Enum as SQLEnum, Integer, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from app.config import settings
from app.models import AgentStatus, EvidenceStatus, ClaimStatus, UserRole

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class AgentDB(Base):
    __tablename__ = "agents"

    agent_id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    role = Column(String)
    status = Column(SQLEnum(AgentStatus), default=AgentStatus.REGISTERED)
    description = Column(String, nullable=True)
    capabilities = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EvidenceDB(Base):
    __tablename__ = "evidence"

    evidence_id = Column(String, primary_key=True, index=True)
    source = Column(String)
    content = Column(String)
    verified = Column(Boolean, default=False)
    status = Column(SQLEnum(EvidenceStatus), default=EvidenceStatus.PENDING)
    submitted_by = Column(String, nullable=True)
    verified_by = Column(String, nullable=True)
    tags = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ClaimDB(Base):
    __tablename__ = "claims"

    claim_id = Column(String, primary_key=True, index=True)
    statement = Column(String)
    status = Column(SQLEnum(ClaimStatus), default=ClaimStatus.SUBMITTED)
    approved = Column(Boolean, default=False)
    reason = Column(String)
    required_evidence_ids = Column(JSON, default=[])
    submitted_by = Column(String, nullable=True)
    evaluated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    evaluated_at = Column(DateTime, nullable=True)


class WorkflowDB(Base):
    __tablename__ = "workflows"

    workflow_id = Column(String, primary_key=True, index=True)
    name = Column(String)
    description = Column(String, nullable=True)
    steps = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.VIEWER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLogDB(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String, nullable=False)
    actor = Column(String, nullable=False)
    target = Column(String, nullable=True)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


class ClaimAuditLogDB(Base):
    __tablename__ = "claim_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(String, index=True, nullable=False)
    action = Column(String, nullable=False)
    actor = Column(String, nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
