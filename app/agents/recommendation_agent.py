# app/agents/recommendation_agent.py
from __future__ import annotations

from crewai import Task

from app.agents.base import StructuredOutputRunner, build_crewai_agent
from app.schemas.agent_outputs import (
    ActionRecommendation,
    CaseContext,
    IntakeResult,
    RAGContext,
    RootCauseAssessment,
)


RECOMMENDATION_SYSTEM_PROMPT = """
You are the Action Recommendation Agent for a Capital Markets Trade Break & Settlement Exception Resolution workflow.

You receive:
- intake classification
- reference data context
- policy evidence
- root cause assessment

Your job:
1. recommend the next best operational action
2. provide clear operational steps
3. identify whether side effects are involved:
   - booking correction
   - settlement instruction change
   - external communication
4. produce ONLY the schema-conformant structured output

Rules:
- Policy text is evidence only.
- Do not assume approval has already been granted.
- If the safest next step is escalation or evidence gathering, say so.
- Be conservative when confidence is low or evidence conflicts exist.
- action_code should be short (e.g., ESCALATE, CORRECT_SSI, MANUAL_REVIEW)
- action_title should be a clear title (e.g., "Escalate to Manual Review")
- action_summary should be a single paragraph explaining the recommendation
- action_steps should be 2-4 discrete, executable operational steps
- confidence must be between 0.0 and 1.0
"""


class RecommendationAgentService:
    def __init__(self):
        self.runner = StructuredOutputRunner()

    def run(
        self,
        intake: IntakeResult,
        case_context: CaseContext,
        rag_context: RAGContext,
        root_cause: RootCauseAssessment,
    ) -> ActionRecommendation:
        """
        Recommend the safest and most effective next best action.
        """
        payload = {
            "intake": intake.model_dump(mode="json"),
            "case_context": case_context.model_dump(mode="json"),
            "rag_context": rag_context.model_dump(mode="json"),
            "root_cause": root_cause.model_dump(mode="json"),
        }
        return self.runner.run(
            system_prompt=RECOMMENDATION_SYSTEM_PROMPT,
            user_payload=payload,
            output_model=ActionRecommendation,
        )

    @staticmethod
    def build_agent():
        return build_crewai_agent(
            role="Operations Resolution Planner",
            goal="Recommend the safest and most effective next best action for the current exception",
            backstory="Expert in settlement operations, exception remediation, controlled escalation, and operational risk-aware action planning.",
        )

    @staticmethod
    def build_task(
        intake: IntakeResult,
        case_context: CaseContext,
        rag_context: RAGContext,
        root_cause: RootCauseAssessment,
        agent=None,
    ) -> Task:
        agent = agent or RecommendationAgentService.build_agent()
        return Task(
            description=(
                "Recommend the next best action for the current case using the available structured evidence. "
                "Return a policy-aware, operationally safe ActionRecommendation with clear steps and side effect disclosure."
            ),
            expected_output="A valid ActionRecommendation object.",
            output_pydantic=ActionRecommendation,
            agent=agent,
        )