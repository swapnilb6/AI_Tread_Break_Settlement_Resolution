# app/policy/approval_policy.py
from __future__ import annotations

from app.schemas.agent_outputs import (
    ActionRecommendation,
    ApprovalDecision,
    CaseContext,
    IntakeResult,
    PolicyCheckResult,
    RAGContext,
    RootCauseAssessment,
)

LOW_CONFIDENCE_THRESHOLD = 0.70
ROOT_CAUSE_CONFIDENCE_THRESHOLD = 0.70
POLICY_RETRIEVAL_STRENGTH_THRESHOLD = 0.55


def evaluate_approval_policy(
    intake: IntakeResult,
    case_context: CaseContext,
    rag_context: RAGContext,
    root_cause: RootCauseAssessment,
    recommendation: ActionRecommendation,
) -> ApprovalDecision:
    """
    Deterministic HITL approval policy.
    
    Returns ApprovalDecision with:
    - status: AUTO_APPROVED, REVIEW_REQUIRED, or BLOCKED
    - requires_human_approval: bool
    - route_to: NONE, OPS_REVIEWER, SUPERVISOR, or RISK_CONTROL
    - reasons: list of strings explaining why HITL is needed
    - policy_checks: list of PolicyCheckResult for each rule
    """
    checks: list[PolicyCheckResult] = []
    reasons: list[str] = []

    def add_check(rule_name: str, passed: bool, reason: str) -> None:
        checks.append(
            PolicyCheckResult(rule_name=rule_name, passed=passed, reason=reason)
        )
        if not passed:
            reasons.append(reason)

    # 1. Intake confidence threshold
    add_check(
        "intake_confidence_threshold",
        intake.exception_type_confidence >= LOW_CONFIDENCE_THRESHOLD,
        f"intake confidence {intake.exception_type_confidence:.2f} below threshold {LOW_CONFIDENCE_THRESHOLD}",
    )

    # 2. Recommendation confidence threshold
    add_check(
        "recommendation_confidence_threshold",
        recommendation.confidence >= LOW_CONFIDENCE_THRESHOLD,
        f"recommendation confidence {recommendation.confidence:.2f} below threshold {LOW_CONFIDENCE_THRESHOLD}",
    )

    # 3. Root cause confidence threshold
    add_check(
        "root_cause_confidence_threshold",
        root_cause.confidence >= ROOT_CAUSE_CONFIDENCE_THRESHOLD,
        f"root cause confidence {root_cause.confidence:.2f} below threshold {ROOT_CAUSE_CONFIDENCE_THRESHOLD}",
    )

    # 4. Risk not HIGH
    add_check(
        "risk_not_high",
        intake.risk != "HIGH",
        f"risk is HIGH",
    )

    # 5. Exception type is known
    add_check(
        "exception_type_known",
        intake.exception_type.upper() != "UNKNOWN",
        "exception type is UNKNOWN",
    )

    # 6. Booking correction side effect check
    add_check(
        "booking_correction_side_effect",
        recommendation.booking_correction_required is False,
        "recommended action impacts booking correction (risky side effect)",
    )

    # 7. Settlement instruction change side effect check
    add_check(
        "settlement_instruction_change_side_effect",
        recommendation.settlement_instruction_change_required is False,
        "recommended action impacts settlement instruction change (risky side effect)",
    )

    # 8. External communication side effect check
    add_check(
        "external_communication_side_effect",
        recommendation.external_communication_required is False,
        "recommended action suggests external communication (requires coordination)",
    )

    # 9. Evidence completeness
    add_check(
        "evidence_complete",
        case_context.evidence_complete is True,
        "evidence is incomplete (missing critical reference data)",
    )

    # 10. Policy retrieval strength
    add_check(
        "policy_retrieval_strength",
        rag_context.retrieval_strength >= POLICY_RETRIEVAL_STRENGTH_THRESHOLD
        and not rag_context.weak_policy_retrieval,
        f"policy retrieval is weak (strength {rag_context.retrieval_strength:.2f} below {POLICY_RETRIEVAL_STRENGTH_THRESHOLD})",
    )

    # 11. Policy contradictions
    add_check(
        "policy_contradictions",
        len(rag_context.policy_contradictions) == 0,
        f"policy contradictions exist: {'; '.join(rag_context.policy_contradictions[:2])}",
    )

    # 12. Data source conflicts
    add_check(
        "data_conflicts",
        len(case_context.data_conflicts) == 0 and len(root_cause.unresolved_conflicts) == 0,
        f"data conflicts detected: {'; '.join((case_context.data_conflicts + root_cause.unresolved_conflicts)[:2])}",
    )

    # 13. No suspected prompt injection
    add_check(
        "no_prompt_injection",
        intake.suspected_prompt_injection is False,
        "suspected prompt injection detected in intake notes",
    )

    # Determine routing based on failure reasons and risk level
    requires_human = len(reasons) > 0

    # High-risk blocking scenarios
    if "data conflicts detected" in " ".join(reasons) and intake.risk == "HIGH":
        status = "BLOCKED"
        route_to = "RISK_CONTROL"
    # High-risk review scenarios
    elif requires_human and intake.risk == "HIGH":
        status = "REVIEW_REQUIRED"
        route_to = "SUPERVISOR"
    # Medium/Low risk review scenarios
    elif requires_human:
        status = "REVIEW_REQUIRED"
        route_to = "OPS_REVIEWER"
    # All policies passed
    else:
        status = "AUTO_APPROVED"
        route_to = "NONE"

    return ApprovalDecision(
        case_id=intake.case_id,
        status=status,
        requires_human_approval=requires_human,
        route_to=route_to,
        reasons=reasons,
        policy_checks=checks,
    )