# app/orchestration/tasks.py
from __future__ import annotations

from app.agents.audit_agent import AuditAgentService
from app.agents.hitl_agent import HITLAgentService
from app.agents.intake_agent import IntakeAgentService
from app.agents.policy_rag_agent import PolicyRAGAgentService
from app.agents.recommendation_agent import RecommendationAgentService
from app.agents.retrieval_agent import RetrievalAgentService
from app.agents.root_cause_agent import RootCauseAgentService
from app.schemas.agent_outputs import (
    ActionRecommendation,
    ApprovalDecision,
    CaseContext,
    IntakeResult,
    RAGContext,
    RootCauseAssessment,
)


def build_intake_task(payload: dict):
    return IntakeAgentService.build_task(payload)


def build_retrieval_task(intake: IntakeResult):
    return RetrievalAgentService.build_task(intake)


def build_rag_task(intake: IntakeResult, case_context: CaseContext):
    return PolicyRAGAgentService.build_task(intake, case_context)


def build_root_cause_task(
    intake: IntakeResult,
    case_context: CaseContext,
    rag_context: RAGContext,
):
    return RootCauseAgentService.build_task(intake, case_context, rag_context)


def build_recommendation_task(
    intake: IntakeResult,
    case_context: CaseContext,
    rag_context: RAGContext,
    root_cause: RootCauseAssessment,
):
    return RecommendationAgentService.build_task(
        intake, case_context, rag_context, root_cause
    )


def build_hitl_task(
    intake: IntakeResult,
    case_context: CaseContext,
    rag_context: RAGContext,
    root_cause: RootCauseAssessment,
    recommendation: ActionRecommendation,
):
    return HITLAgentService.build_task(
        intake, case_context, rag_context, root_cause, recommendation
    )


def build_audit_task(
    intake: IntakeResult,
    case_context: CaseContext,
    rag_context: RAGContext,
    root_cause: RootCauseAssessment,
    recommendation: ActionRecommendation,
    approval: ApprovalDecision,
):
    return AuditAgentService.build_task(
        intake, case_context, rag_context, root_cause, recommendation, approval
    )