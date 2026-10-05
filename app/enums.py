from enum import Enum


class AgentStatus(str, Enum):
    REGISTERED = "registered"
    ACTIVE = "active"
    PAUSED = "paused"
    RETIRED = "retired"


class EvidenceStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class ClaimStatus(str, Enum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class UserRole(str, Enum):
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"
