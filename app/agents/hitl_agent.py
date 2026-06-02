# app/agents/hitl_agent.py
from __future__ import annotations

from crewai import Task

from app.agents.base import build_crewai_agent
from app.policy.approval_policy import evaluate_approval_policy
from app.schemas.agent_outputs import (
    ActionRecommendation,
    ApprovalDecision,
    CaseContext,
    IntakeResult,
    RAGContext,
    RootCauseAssessment,
)


class HITLAgentService:
    """
    Human-In-The-Loop (HITL) approval controller.
    
    Applies deterministic approval policy rules and routes cases to appropriate reviewers
    based on risk level, confidence thresholds, and operational constraints.
    """
    
    def run(
        self,
        intake: IntakeResult,
        case_context: CaseContext,
        rag_context: RAGContext,
        root_cause: RootCauseAssessment,
        recommendation: ActionRecommendation,
    ) -> ApprovalDecision:
        """
        Evaluate approval policy and determine HITL routing.
        
        Returns ApprovalDecision with routing:
        - AUTO_APPROVED / NONE: No human review needed
        - REVIEW_REQUIRED / OPS_REVIEWER: Standard review queue
        - REVIEW_REQUIRED / SUPERVISOR: High-risk escalation
        - BLOCKED / RISK_CONTROL: Blocking issues detected
        """
        return evaluate_approval_policy(
            intake=intake,
            case_context=case_context,
            rag_context=rag_context,
            root_cause=root_cause,
            recommendation=recommendation,
        )

    @staticmethod
    def build_agent():
        return build_crewai_agent(
            role="Approval Policy Controller",
            goal="Apply deterministic approval policy and route cases requiring human review",
            backstory="This controller enforces coded approval policy, risk gating, and HITL branching for sensitive operations.",
        )

    @staticmethod
    def build_task(
        intake: IntakeResult,
        case_context: CaseContext,
        rag_context: RAGContext,
        root_cause: RootCauseAssessment,
        recommendation: ActionRecommendation,
        agent=None,
    ) -> Task:
        agent = agent or HITLAgentService.build_agent()
        return Task(
            description=(
                "Apply deterministic approval policy to the current case and return a valid ApprovalDecision. "
                "Route to the appropriate reviewer or queue based on risk level, confidence thresholds, and operational constraints."
            ),
            expected_output="A valid ApprovalDecision object.",
            output_pydantic=ApprovalDecision,
            agent=agent,
        )