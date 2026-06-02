from datetime import datetime
from typing import Any

from pydantic import Field

from app.schemas.common import (
    StrictBaseModel,
    RiskLevel,
    ApprovalStatus,
    CaseStatus,
    ExceptionType,
    Citation,
)


class IntakeResult(StrictBaseModel):
    case_id: str
    exception_type: ExceptionType
    summary: str
    extracted_entities: dict[str, Any] = Field(default_factory=dict)
    missing_fields: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)


class CaseContext(StrictBaseModel):
    case_id: str
    status: CaseStatus = CaseStatus.NEW
    intake: IntakeResult
    trade_data: dict[str, Any] = Field(default_factory=dict)
    settlement_data: dict[str, Any] = Field(default_factory=dict)
    ssi_data: dict[str, Any] = Field(default_factory=dict)
    counterparty_data: dict[str, Any] = Field(default_factory=dict)
    market_calendar_data: dict[str, Any] = Field(default_factory=dict)
    similar_cases: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class RAGContext(StrictBaseModel):
    case_id: str
    query: str
    retrieved_chunks: list[str] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    retrieval_confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    contradictions_found: bool = False


class RootCauseAssessment(StrictBaseModel):
    case_id: str
    likely_root_cause: str
    alternative_causes: list[str] = Field(default_factory=list)
    evidence_gaps: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    citations: list[Citation] = Field(default_factory=list)


class ActionRecommendation(StrictBaseModel):
    case_id: str
    recommended_action: str
    rationale: str
    risk: RiskLevel
    requires_human_approval: bool
    draft_note: str
    confidence: float = Field(ge=0.0, le=1.0)
    citations: list[Citation] = Field(default_factory=list)


class ApprovalDecision(StrictBaseModel):
    case_id: str
    status: ApprovalStatus
    approver_id: str | None = None
    approver_comments: str | None = None
    corrected_action: str | None = None
    decided_at: datetime | None = None


class AuditRecord(StrictBaseModel):
    case_id: str
    exception_type: ExceptionType
    final_status: CaseStatus
    risk: RiskLevel
    tool_trace: list[str] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)