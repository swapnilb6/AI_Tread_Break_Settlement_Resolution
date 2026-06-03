# app/repositories/memory_repo.py
from __future__ import annotations

from collections import Counter
from typing import List

from sqlalchemy.orm import Session

from app.db import models as db_models
from app.schemas.memory import (
    ApprovalHistoryEntry,
    ApprovalPatternStats,
    HistoricalCaseSummary,
)


class MemoryRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_similar_resolved_cases(
        self,
        exception_type: str | None,
        market: str | None,
        counterparty_id: str | None,
        limit: int = 10,
    ) -> List[HistoricalCaseSummary]:
        """
        Adapt this query to your actual ORM models.
        Expected source: resolved historical cases / audit records / case table.
        """
        rows = []

        # Example patch-friendly pattern:
        if hasattr(db_models, "ResolutionHistory"):
            query = self.session.query(db_models.ResolutionHistory)
            if exception_type:
                query = query.filter(db_models.ResolutionHistory.exception_type == exception_type)
            if market and hasattr(db_models.ResolutionHistory, "market"):
                query = query.filter(db_models.ResolutionHistory.market == market)
            if counterparty_id and hasattr(db_models.ResolutionHistory, "counterparty_id"):
                query = query.filter(db_models.ResolutionHistory.counterparty_id == counterparty_id)

            rows = query.limit(limit).all()

            results = []
            for row in rows:
                similarity_score = 0.4
                if getattr(row, "exception_type", None) == exception_type:
                    similarity_score += 0.3
                if getattr(row, "market", None) == market:
                    similarity_score += 0.2
                if getattr(row, "counterparty_id", None) == counterparty_id:
                    similarity_score += 0.1

                results.append(
                    HistoricalCaseSummary(
                        case_id=str(getattr(row, "case_id", "")),
                        exception_type=getattr(row, "exception_type", None),
                        market=getattr(row, "market", None),
                        counterparty_id=getattr(row, "counterparty_id", None),
                        root_cause=getattr(row, "root_cause", None),
                        action_code=getattr(row, "action_code", None),
                        final_status=getattr(row, "status", None),
                        resolved_at_utc=getattr(row, "resolved_at_utc", None),
                        similarity_score=min(similarity_score, 1.0),
                        support_signals=[
                            signal
                            for signal in [
                                "same exception_type" if getattr(row, "exception_type", None) == exception_type else None,
                                "same market" if getattr(row, "market", None) == market else None,
                                "same counterparty" if getattr(row, "counterparty_id", None) == counterparty_id else None,
                            ]
                            if signal
                        ],
                    )
                )
            return sorted(results, key=lambda x: x.similarity_score, reverse=True)

        return []

    def get_approval_history(
        self,
        exception_type: str | None,
        action_code: str | None = None,
        limit: int = 20,
    ) -> List[ApprovalHistoryEntry]:
        """
        Adapt to your actual approval/audit model names.
        """
        if not hasattr(db_models, "Approval"):
            return []

        query = self.session.query(db_models.Approval)

        if exception_type and hasattr(db_models.Approval, "exception_type"):
            query = query.filter(db_models.Approval.exception_type == exception_type)

        if action_code and hasattr(db_models.Approval, "action_code"):
            query = query.filter(db_models.Approval.action_code == action_code)

        rows = query.limit(limit).all()

        results = []
        for row in rows:
            reviewer_decision = getattr(row, "reviewer_decision", None)
            status = getattr(row, "status", None)
            override_flag = reviewer_decision in {"REJECTED", "APPROVED"} and status == "REVIEW_REQUIRED"

            results.append(
                ApprovalHistoryEntry(
                    case_id=str(getattr(row, "case_id", "")),
                    reviewer_name=getattr(row, "reviewer_name", None),
                    reviewer_decision=reviewer_decision,
                    reviewer_comments=getattr(row, "reviewer_comments", None),
                    route_to=getattr(row, "route_to", None),
                    action_code=getattr(row, "action_code", None),
                    override_flag=override_flag,
                    decided_at_utc=getattr(row, "updated_at_utc", None),
                )
            )

        return results

    def build_approval_stats(
        self,
        approval_history: List[ApprovalHistoryEntry],
    ) -> ApprovalPatternStats:
        total = len(approval_history)
        approvals = sum(1 for x in approval_history if x.reviewer_decision == "APPROVED")
        rejections = sum(1 for x in approval_history if x.reviewer_decision == "REJECTED")
        overrides = sum(1 for x in approval_history if x.override_flag)

        rejection_comments = [
            x.reviewer_comments.strip()
            for x in approval_history
            if x.reviewer_decision == "REJECTED" and x.reviewer_comments
        ]
        reason_counts = Counter(rejection_comments).most_common(5)

        return ApprovalPatternStats(
            total_reviews=total,
            approvals=approvals,
            rejections=rejections,
            override_count=overrides,
            approval_rate=(approvals / total) if total else 0.0,
            rejection_rate=(rejections / total) if total else 0.0,
            override_rate=(overrides / total) if total else 0.0,
            top_rejection_reasons=[reason for reason, _ in reason_counts],
        )