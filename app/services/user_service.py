from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.database import AuditLogDB, ClaimAuditLogDB, UserDB
from app.models import AuditLogEntry, UserCreate, UserOut, UserRole


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user_in: UserCreate, hashed_password: str) -> UserOut:
        user = UserDB(
            username=user_in.username,
            hashed_password=hashed_password,
            role=user_in.role,
            is_active=True,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return UserOut.from_orm(user)

    def get_user_by_username(self, username: str) -> Optional[UserDB]:
        return self.db.query(UserDB).filter(UserDB.username == username).first()

    def get_user_by_id(self, user_id: int) -> Optional[UserDB]:
        return self.db.query(UserDB).filter(UserDB.id == user_id).first()

    def list_users(self) -> List[UserOut]:
        return [UserOut.from_orm(user) for user in self.db.query(UserDB).all()]


class AuditService:
    @staticmethod
    def log_action(db: Session, actor: str, action: str, target: str = None, details: str = None):
        entry = AuditLogDB(
            actor=actor,
            action=action,
            target=target,
            details=details,
            timestamp=datetime.utcnow(),
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return AuditLogEntry.from_orm(entry)

    @staticmethod
    def log_claim_timeline(db: Session, claim_id: str, actor: str, action: str, details: str = None):
        entry = ClaimAuditLogDB(
            claim_id=claim_id,
            actor=actor,
            action=action,
            details=details,
            created_at=datetime.utcnow(),
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry

    @staticmethod
    def get_audit_logs(db: Session, target: Optional[str] = None) -> List[AuditLogEntry]:
        query = db.query(AuditLogDB)
        if target:
            query = query.filter(AuditLogDB.target == target)
        return [AuditLogEntry.from_orm(item) for item in query.order_by(AuditLogDB.timestamp.desc()).all()]

    @staticmethod
    def get_claim_timeline(db: Session, claim_id: str):
        return db.query(ClaimAuditLogDB).filter(ClaimAuditLogDB.claim_id == claim_id).order_by(ClaimAuditLogDB.created_at.asc()).all()


audit_service = AuditService()
