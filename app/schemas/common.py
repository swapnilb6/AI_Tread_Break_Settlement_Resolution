from enum import Enum
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Any


class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ApprovalStatus(str, Enum):
    NOT_REQUIRED = "NOT_REQUIRED"
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class CaseStatus(str, Enum):
    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    RESOLVED = "RESOLVED"
    REJECTED = "REJECTED"


class ExceptionType(str, Enum):
    FAILED_SETTLEMENT = "FAILED_SETTLEMENT"
    SSI_MISMATCH = "SSI_MISMATCH"
    COUNTERPARTY_MISMATCH = "COUNTERPARTY_MISMATCH"
    HOLIDAY_ISSUE = "HOLIDAY_ISSUE"
    BOOKING_BREAK = "BOOKING_BREAK"
    UNKNOWN = "UNKNOWN"


class Citation(StrictBaseModel):
    doc_name: str
    section_heading: str | None = None
    source_path: str | None = None
    chunk_id: str | None = None


class APIResponse(StrictBaseModel):
    success: bool
    message: str
    data: dict[str, Any] | None = None
    timestamp: datetime = datetime.utcnow()