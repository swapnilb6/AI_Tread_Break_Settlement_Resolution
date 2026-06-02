# app/schemas/agent_outputs.py# app/schemasfrom __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class StrictBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        populate_by_name=True,
        arbitrary_types_allowed=False,
    )


class ToolExecutionRecord(StrictBaseModel):
    tool_name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    status: Literal["SUCCESS", "ERROR"]
    record_count: int = 0
    output_summary: Optional[str] = None
    error_message: Optional[str] = None
    executed_at_utc: datetime = Field(default_factory=utc_now)


class DataEvidenceRef(StrictBaseModel):
    source_type: Literal[
        "trade",
        "settlement",
        "ssi",
        "counterparty",
        "calendar",
        "history",
        "ops_note",
        "policy_chunk",
    ]
    source_id: str
    description: str
    fields_used: List[str] = Field(default_factory=list)


class PolicyEvidence(StrictBaseModel):
    doc_name: str
    doc_type: Optional[str] = None
    section_heading: Optional[str] = None
    exception_type: Optional[str] = None
    market: Optional[str] = None
    version: Optional[str] = None
    effective_date: Optional[str] = None
    source_path: Optional[str] = None
    excerpt: str
    relevance_score: float = Field(ge=0.0, le=1.0)
    evidence_id: str


class IntakeResult(StrictBaseModel):
    case_id: str
    trade_id: Optional[str] = None
    exception_id: Optional[str] = None
    exception_type: str
    exception_type_confidence: float = Field(ge=0.0, le=1.0)
    risk: Literal["LOW", "MEDIUM", "HIGH"]
    market: Optional[str] = None
    counterparty_id: Optional[str] = None
    normalized_summary: str
    extracted_entities: Dict[str, str] = Field(default_factory=dict)
    missing_fields: List[str] = Field(default_factory=list)
    suspected_prompt_injection: bool = False
    requires_manual_review: bool = False
    review_reasons: List[str] = Field(default_factory=list)


class CaseContext(StrictBaseModel):
    case_id: str
    trade: Optional[Dict[str, Any]] = None
    settlement: Optional[Dict[str, Any]] = None
    ssi: Optional[Dict[str, Any]] = None
    counterparty: Optional[Dict[str, Any]] = None
    market_calendar: Optional[Dict[str, Any]] = None
    similar_cases: List[Dict[str, Any]] = Field(default_factory=list)
    ops_notes: List[Dict[str, Any]] = Field(default_factory=list)
    evidence_complete: bool
    data_conflicts: List[str] = Field(default_factory=list)
    retrieval_strength: float = Field(ge=0.0, le=1.0)
    evidence_refs: List[DataEvidenceRef] = Field(default_factory=list)
    tool_trace: List[ToolExecutionRecord] = Field(default_factory=list)


class RAGContext(StrictBaseModel):
    case_id: str
    query_used: str
    retrieved_policies: List[PolicyEvidence] = Field(default_factory=list)
    weak_policy_retrieval: bool
    policy_contradictions: List[str] = Field(default_factory=list)
    retrieval_strength: float = Field(ge=0.0, le=1.0)
    evidence_refs: List[DataEvidenceRef] = Field(default_factory=list)
    tool_trace: List[ToolExecutionRecord] = Field(default_factory=list)


class RootCauseAssessment(StrictBaseModel):
    case_id: str
    likely_root_cause: str
    confidence: float = Field(ge=0.0, le=1.0)
    contributing_factors: List[str] = Field(default_factory=list)
    alternative_causes: List[str] = Field(default_factory=list)
    evidence_refs: List[str] = Field(default_factory=list)
    unresolved_conflicts: List[str] = Field(default_factory=list)


class ActionRecommendation(StrictBaseModel):
    case_id: str
    action_code: str
    action_title: str
    action_summary: str
    action_steps: List[str] = Field(default_factory=list)
    booking_correction_required: bool = False
    settlement_instruction_change_required: bool = False
    external_communication_required: bool = False
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_refs: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class PolicyCheckResult(StrictBaseModel):
    rule_name: str
    passed: bool
    reason: str


class ApprovalDecision(StrictBaseModel):
    case_id: str
    status: Literal["AUTO_APPROVED", "REVIEW_REQUIRED", "BLOCKED"]
    requires_human_approval: bool
    route_to: Literal["NONE", "OPS_REVIEWER", "SUPERVISOR", "RISK_CONTROL"]
    reasons: List[str] = Field(default_factory=list)
    policy_checks: List[PolicyCheckResult] = Field(default_factory=list)


class AuditRecord(StrictBaseModel):
    case_id: str
    generated_at_utc: datetime = Field(default_factory=utc_now)
    case_status: Literal["ANALYZED", "PENDING_APPROVAL", "AUTO_APPROVED", "BLOCKED"]
    intake_result: IntakeResult
    case_context: CaseContext
    rag_context: RAGContext
    root_cause: RootCauseAssessment
    recommendation: ActionRecommendation
    approval: ApprovalDecision
    audit_version: str = "1.0"
