# app/services/memory_service.py
from __future__ import annotations

from typing import List

from app.db.session import SessionLocal
from app.schemas.agent_outputs import IntakeResult, CaseContext
from app.schemas.memory import MemoryContext
from app.repositories.memory_repo import MemoryRepository


class MemoryService:
    def build_memory_context(
        self,
        intake: IntakeResult,
        case_context: CaseContext,
        proposed_action_code: str | None = None,
    ) -> MemoryContext:
        session = SessionLocal()
        try:
            repo = MemoryRepository(session)

            episodic_cases = repo.get_similar_resolved_cases(
                exception_type=intake.exception_type,
                market=intake.market,
                counterparty_id=intake.counterparty_id,
                limit=10,
            )

            approval_history = repo.get_approval_history(
                exception_type=intake.exception_type,
                action_code=proposed_action_code,
                limit=20,
            )

            approval_stats = repo.build_approval_stats(approval_history)

            recommendation_hints: List[str] = []
            safety_notes: List[str] = []

            if episodic_cases:
                top = episodic_cases[:3]
                common_actions = [x.action_code for x in top if x.action_code]
                common_root_causes = [x.root_cause for x in top if x.root_cause]

                if common_actions:
                    recommendation_hints.append(
                        f"Top similar cases commonly resolved with actions: {', '.join(common_actions[:3])}"
                    )
                if common_root_causes:
                    recommendation_hints.append(
                        f"Top similar cases commonly had root causes: {', '.join(common_root_causes[:3])}"
                    )

            if approval_stats.total_reviews >= 3:
                safety_notes.append(
                    f"Approval memory available: {approval_stats.total_reviews} prior reviews for similar cases"
                )

            if approval_stats.rejection_rate >= 0.40:
                safety_notes.append(
                    "Similar cases show elevated rejection rate; be conservative and prefer HITL when uncertain"
                )

            if approval_stats.override_rate >= 0.30:
                safety_notes.append(
                    "High override rate observed in similar approvals; do not over-trust historical action patterns"
                )

            return MemoryContext(
                case_id=intake.case_id,
                episodic_cases=episodic_cases,
                approval_history=approval_history,
                approval_pattern_stats=approval_stats,
                recommendation_hints=recommendation_hints,
                safety_notes=safety_notes,
            )
        finally:
            session.close()