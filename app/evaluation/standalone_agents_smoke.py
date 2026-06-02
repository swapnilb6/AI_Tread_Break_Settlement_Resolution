# app/evaluation/standalone_agents_smoke.py
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from app.agents.audit_agent import AuditAgentService
from app.agents.hitl_agent import HITLAgentService
from app.agents.intake_agent import IntakeAgentService
from app.agents.policy_rag_agent import PolicyRAGAgentService
from app.agents.recommendation_agent import RecommendationAgentService
from app.agents.retrieval_agent import RetrievalAgentService
from app.agents.root_cause_agent import RootCauseAgentService


def load_one_exception_row() -> dict:
    csv_path = Path("data/trade_exceptions.csv")
    df = pd.read_csv(csv_path)
    row = df.iloc[0].to_dict()
    # normalize NaN to None
    return {k: (None if pd.isna(v) else v) for k, v in row.items()}


def main():
    payload = load_one_exception_row()

    intake_agent = IntakeAgentService()
    retrieval_agent = RetrievalAgentService()
    rag_agent = PolicyRAGAgentService()
    root_cause_agent = RootCauseAgentService()
    recommendation_agent = RecommendationAgentService()
    hitl_agent = HITLAgentService()
    audit_agent = AuditAgentService()

    intake = intake_agent.run(payload)
    case_context = retrieval_agent.run(intake)
    rag_context = rag_agent.run(intake, case_context)
    root_cause = root_cause_agent.run(intake, case_context, rag_context)
    recommendation = recommendation_agent.run(intake, case_context, rag_context, root_cause)
    approval = hitl_agent.run(intake, case_context, rag_context, root_cause, recommendation)
    audit = audit_agent.run(intake, case_context, rag_context, root_cause, recommendation, approval)

    print("\n=== IntakeResult ===")
    print(json.dumps(intake.model_dump(mode="json"), indent=2, default=str))

    print("\n=== CaseContext ===")
    print(json.dumps(case_context.model_dump(mode="json"), indent=2, default=str))

    print("\n=== RAGContext ===")
    print(json.dumps(rag_context.model_dump(mode="json"), indent=2, default=str))

    print("\n=== RootCauseAssessment ===")
    print(json.dumps(root_cause.model_dump(mode="json"), indent=2, default=str))

    print("\n=== ActionRecommendation ===")
    print(json.dumps(recommendation.model_dump(mode="json"), indent=2, default=str))

    print("\n=== ApprovalDecision ===")
    print(json.dumps(approval.model_dump(mode="json"), indent=2, default=str))

    print("\n=== AuditRecord ===")
    print(json.dumps(audit.model_dump(mode="json"), indent=2, default=str))


if __name__ == "__main__":
    main()