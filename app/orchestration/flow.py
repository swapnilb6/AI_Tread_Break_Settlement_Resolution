from app.schemas.case import CaseContext, RAGContext, RootCauseAssessment, ActionRecommendation
from app.schemas.common import RiskLevel


class ExceptionResolutionFlow:
    """
    Phase 1 skeleton.
    Next phase will wire this into CrewAI Flow steps and agent tasks.
    """

    def run(self, case: CaseContext) -> dict:
        rag_context = self._retrieve_policy(case)
        root_cause = self._assess_root_cause(case, rag_context)
        recommendation = self._recommend_action(case, root_cause)

        return {
            "case": case.model_dump(),
            "rag_context": rag_context.model_dump(),
            "root_cause": root_cause.model_dump(),
            "recommendation": recommendation.model_dump(),
            "approval_required": self._approval_required(recommendation),
        }

    def _retrieve_policy(self, case: CaseContext) -> RAGContext:
        return RAGContext(
            case_id=case.case_id,
            query=f"{case.intake.exception_type} {case.intake.summary}",
            retrieved_chunks=[],
            citations=[],
            retrieval_confidence=0.0,
            contradictions_found=False,
        )

    def _assess_root_cause(self, case: CaseContext, rag_context: RAGContext) -> RootCauseAssessment:
        return RootCauseAssessment(
            case_id=case.case_id,
            likely_root_cause="INSUFFICIENT_DATA",
            alternative_causes=[],
            evidence_gaps=["Trade retrieval not yet implemented", "RAG evidence not yet implemented"],
            confidence=0.25,
            citations=[],
        )

    def _recommend_action(
        self,
        case: CaseContext,
        root_cause: RootCauseAssessment,
    ) -> ActionRecommendation:
        return ActionRecommendation(
            case_id=case.case_id,
            recommended_action="Route to manual review queue",
            rationale="Foundation phase placeholder recommendation.",
            risk=RiskLevel.MEDIUM,
            requires_human_approval=True,
            draft_note="Case requires further enrichment before automated recommendation.",
            confidence=0.30,
            citations=[],
        )

    def _approval_required(self, recommendation: ActionRecommendation) -> bool:
        return (
            recommendation.requires_human_approval
            or recommendation.risk == RiskLevel.HIGH
            or recommendation.confidence < 0.75
        )