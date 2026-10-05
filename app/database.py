from sqlalchemy import create_engine, Column, String, Boolean, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from app.config import settings
from app.models import AgentStatus, EvidenceStatus, ClaimStatus

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


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
