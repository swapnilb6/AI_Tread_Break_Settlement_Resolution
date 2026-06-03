# app/schemas/flow_state.py
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import Field

from app.schemas.agent_outputs import (
    ActionRecommendation,
    ApprovalDecision,
    AuditRecord,
    IntakeResult,
    CaseContext,
    RAGContext,
    RootCauseAssessment,
    StrictBaseModel,
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class FlowStage(str, Enum):
    INTAKE = "INTAKE"
    RETRIEVE_CASE_DATA = "RETRIEVE_CASE_DATA"
    RETRIEVE_POLICY_CONTEXT = "RETRIEVE_POLICY_CONTEXT"
    INFER_ROOT_CAUSE = "INFER_ROOT_CAUSE"
    RECOMMEND_ACTION = "RECOMMEND_ACTION"
    CHECK_APPROVAL_RULES = "CHECK_APPROVAL_RULES"
    REQUEST_HUMAN_APPROVAL = "REQUEST_HUMAN_APPROVAL"
    FINALIZE_DRAFT = "FINALIZE_DRAFT"
    PERSIST_AUDIT_TRAIL = "PERSIST_AUDIT_TRAIL"
    RETURN_FINAL_SUMMARY = "RETURN_FINAL_SUMMARY"


class WorkflowStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    RUNNING = "RUNNING"
    PENDING_HUMAN_APPROVAL = "PENDING_HUMAN_APPROVAL"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"


class ReviewerDecision(str, Enum):
    NOT_REQUIRED = "NOT_REQUIRED"
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class FlowEvent(StrictBaseModel):
    timestamp_utc: datetime = Field(default_factory=utc_now)
    stage: FlowStage
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)


class HumanApprovalRequest(StrictBaseModel):
    approved: bool
    reviewer_name: str
    reviewer_comments: str


class FinalCaseSummary(StrictBaseModel):
    case_id: str
    flow_id: str
    workflow_status: WorkflowStatus
    current_stage: FlowStage
    approval_status: str
    requires_human_approval: bool
    reviewer_decision: ReviewerDecision
    route_to: str
    exception_type: Optional[str] = None
    risk: Optional[str] = None
    root_cause: Optional[str] = None
    root_cause_confidence: Optional[float] = None
    recommended_action: Optional[str] = None
    recommendation_confidence: Optional[float] = None
    pending_reasons: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    audit_record_id: Optional[str] = None
    started_at_utc: datetime
    completed_at_utc: Optional[datetime] = None


class CaseResolutionFlowState(StrictBaseModel):
    flow_id: str = Field(default_factory=lambda: str(uuid4()))
    case_id: Optional[str] = None

    request_payload: Dict[str, Any] = Field(default_factory=dict)

    current_stage: FlowStage = FlowStage.INTAKE
    workflow_status: WorkflowStatus = WorkflowStatus.NOT_STARTED

    reviewer_decision: ReviewerDecision = ReviewerDecision.NOT_REQUIRED
    reviewer_name: Optional[str] = None
    reviewer_comments: Optional[str] = None

    started_at_utc: datetime = Field(default_factory=utc_now)
    updated_at_utc: datetime = Field(default_factory=utc_now)
    completed_at_utc: Optional[datetime] = None

    intake_result: Optional[IntakeResult] = None
    case_context: Optional[CaseContext] = None
    rag_context: Optional[RAGContext] = None
    root_cause: Optional[RootCauseAssessment] = None
    recommendation: Optional[ActionRecommendation] = None
    approval_decision: Optional[ApprovalDecision] = None
    audit_record: Optional[AuditRecord] = None
    final_summary: Optional[FinalCaseSummary] = None

    persisted_case_ref: Optional[str] = None
    persisted_approval_ref: Optional[str] = None
    persisted_audit_ref: Optional[str] = None

    errors: List[str] = Field(default_factory=list)
    event_log: List[FlowEvent] = Field(default_factory=list)