# app/agents/audit_agent.py
from __future__ import annotations

from crewai import Task

from app.agents.base import build_crewai_agent
from app.schemas.agent_outputs import (
    ActionRecommendation,
    ApprovalDecision,
    AuditRecord,
    CaseContext,
    IntakeResult,
    RAGContext,
    RootCauseAssessment,
)


class AuditAgentService:
    """
    Audit recorder. Assembles a complete, auditable case record for persistence and review.
    """
    
    def run(
        self,
        intake: IntakeResult,
        case_context: CaseContext,
        rag_context: RAGContext,
        root_cause: RootCauseAssessment,
        recommendation: ActionRecommendation,
        approval: ApprovalDecision,
    ) -> AuditRecord:
        """
        Assemble final audit-ready case record from all prior structured outputs.
        
        Maps approval status to case status for audit trail:
        - AUTO_APPROVED -> ANALYZED
        - REVIEW_REQUIRED -> PENDING_APPROVAL
        - BLOCKED -> ANALYZED (as a rejected path)
        """
        if approval.status == "AUTO_APPROVED":
            case_status = "ANALYZED"
        elif approval.status == "BLOCKED":
            case_status = "ANALYZED"
        elif approval.requires_human_approval:
            case_status = "PENDING_APPROVAL"
        else:
            case_status = "ANALYZED"

        return AuditRecord(
            case_id=intake.case_id,
            case_status=case_status,
            intake_result=intake,
            case_context=case_context,
            rag_context=rag_context,
            root_cause=root_cause,
            recommendation=recommendation,
            approval=approval,
        )

    @staticmethod
    def build_agent():
        return build_crewai_agent(
            role="Audit Recorder",
            goal="Assemble an audit-ready case record for persistence and review",
            backstory="Expert in operational audit trails, traceability, reproducibility, and structured case record generation.",
        )

    @staticmethod
    def build_task(
        intake: IntakeResult,
        case_context: CaseContext,
        rag_context: RAGContext,
        root_cause: RootCauseAssessment,
        recommendation: ActionRecommendation,
        approval: ApprovalDecision,
        agent=None,
    ) -> Task:
        agent = agent or AuditAgentService.build_agent()
        return Task(
            description=(
                "Assemble the final audit-ready case record from all prior structured outputs. "
                "Include all evidence references, decision points, and routing decisions for full traceability."
            ),
            expected_output="A valid AuditRecord object.",
            output_pydantic=AuditRecord,
            agent=agent,
        )