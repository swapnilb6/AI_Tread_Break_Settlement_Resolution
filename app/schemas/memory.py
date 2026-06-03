# app/schemas/memory.py
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import Field

from app.schemas.agent_outputs import StrictBaseModel


class HistoricalCaseSummary(StrictBaseModel):
    case_id: str
    exception_type: Optional[str] = None
    market: Optional[str] = None
    counterparty_id: Optional[str] = None
    root_cause: Optional[str] = None
    action_code: Optional[str] = None
    final_status: Optional[str] = None
    resolved_at_utc: Optional[datetime] = None
    similarity_score: float = Field(default=0.0, ge=0.0, le=1.0)
    support_signals: List[str] = Field(default_factory=list)


class ApprovalHistoryEntry(StrictBaseModel):
    case_id: str
    reviewer_name: Optional[str] = None
    reviewer_decision: Optional[str] = None
    reviewer_comments: Optional[str] = None
    route_to: Optional[str] = None
    action_code: Optional[str] = None
    override_flag: bool = False
    decided_at_utc: Optional[datetime] = None


class ApprovalPatternStats(StrictBaseModel):
    total_reviews: int = 0
    approvals: int = 0
    rejections: int = 0
    override_count: int = 0
    approval_rate: float = 0.0
    rejection_rate: float = 0.0
    override_rate: float = 0.0
    top_rejection_reasons: List[str] = Field(default_factory=list)


class MemoryContext(StrictBaseModel):
    case_id: str
    episodic_cases: List[HistoricalCaseSummary] = Field(default_factory=list)
    approval_history: List[ApprovalHistoryEntry] = Field(default_factory=list)
    approval_pattern_stats: Optional[ApprovalPatternStats] = None
    recommendation_hints: List[str] = Field(default_factory=list)
    safety_notes: List[str] = Field(default_factory=list)
