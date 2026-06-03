# app/orchestration/flow.py
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from crewai.flow.flow import Flow, listen, router, start
from app.services.memory_service import MemoryService
from app.agents.audit_agent import AuditAgentService
from app.agents.hitl_agent import HITLAgentService
from app.agents.intake_agent import IntakeAgentService
from app.agents.policy_rag_agent import PolicyRAGAgentService
from app.agents.recommendation_agent import RecommendationAgentService
from app.agents.retrieval_agent import RetrievalAgentService
from app.agents.root_cause_agent import RootCauseAgentService
from app.schemas.flow_state import (
    CaseResolutionFlowState,
    FinalCaseSummary,
    FlowEvent,
    FlowStage,
    HumanApprovalRequest,
    ReviewerDecision,
    WorkflowStatus,
)
from app.services.workflow_persistence_service import WorkflowPersistenceService


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class TradeExceptionResolutionFlow(Flow[CaseResolutionFlowState]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.memory_service = MemoryService()

        # Initialize agents
        self.intake_agent = IntakeAgentService()
        self.retrieval_agent = RetrievalAgentService()
        self.rag_agent = PolicyRAGAgentService()
        self.root_cause_agent = RootCauseAgentService()
        self.recommendation_agent = RecommendationAgentService()
        self.hitl_agent = HITLAgentService()
        self.audit_agent = AuditAgentService()
        self.persistence = WorkflowPersistenceService()
        
        # Initialize flow state if not already set
        if not hasattr(self, 'state') or self.state is None:
            self.state = CaseResolutionFlowState()

    # ---------- shared helpers ----------

    def _touch(self) -> None:
        self.state.updated_at_utc = utc_now()

    def _set_stage(self, stage: FlowStage, workflow_status: Optional[WorkflowStatus] = None) -> None:
        self.state.current_stage = stage
        if workflow_status is not None:
            self.state.workflow_status = workflow_status
        self._touch()

    def _event(self, stage: FlowStage, message: str, **details: Any) -> None:
        self.state.event_log.append(
            FlowEvent(stage=stage, message=message, details=details)
        )
        self._touch()

    def _persist_snapshot(self) -> None:
        persisted_case_ref = self.persistence.persist_flow_snapshot(self.state)
        if persisted_case_ref:
            self.state.persisted_case_ref = persisted_case_ref
        self._touch()

    def _build_final_summary(self) -> FinalCaseSummary:
        approval = self.state.approval_decision
        intake = self.state.intake_result
        root_cause = self.state.root_cause
        recommendation = self.state.recommendation

        return FinalCaseSummary(
            case_id=self.state.case_id or "",
            flow_id=self.state.flow_id,
            workflow_status=self.state.workflow_status,
            current_stage=self.state.current_stage,
            approval_status=approval.status if approval else "UNKNOWN",
            requires_human_approval=approval.requires_human_approval if approval else False,
            reviewer_decision=self.state.reviewer_decision,
            route_to=approval.route_to if approval else "NONE",
            exception_type=intake.exception_type if intake else None,
            risk=intake.risk if intake else None,
            root_cause=root_cause.likely_root_cause if root_cause else None,
            root_cause_confidence=root_cause.confidence if root_cause else None,
            recommended_action=recommendation.action_title if recommendation else None,
            recommendation_confidence=recommendation.confidence if recommendation else None,
            pending_reasons=approval.reasons if approval else [],
            warnings=recommendation.warnings if recommendation else [],
            audit_record_id=self.state.persisted_audit_ref,
            started_at_utc=self.state.started_at_utc,
            completed_at_utc=self.state.completed_at_utc,
        )

    def _finalize_audit_and_persist(self) -> None:
        if not all(
            [
                self.state.intake_result,
                self.state.case_context,
                self.state.rag_context,
                self.state.root_cause,
                self.state.recommendation,
                self.state.approval_decision,
            ]
        ):
            raise ValueError("Cannot finalize audit record because required state is incomplete.")

        self.state.audit_record = self.audit_agent.run(
            intake=self.state.intake_result,
            case_context=self.state.case_context,
            rag_context=self.state.rag_context,
            root_cause=self.state.root_cause,
            recommendation=self.state.recommendation,
            approval=self.state.approval_decision,
        )
        self.state.persisted_audit_ref = self.persistence.persist_audit_record(self.state.audit_record)
        self._touch()

    # ---------- flow stages ----------

    @start()
    def intake(self):
        self._set_stage(FlowStage.INTAKE, WorkflowStatus.RUNNING)
        self._event(FlowStage.INTAKE, "Starting intake stage")

        intake_result = self.intake_agent.run(self.state.request_payload)
        self.state.intake_result = intake_result
        self.state.case_id = intake_result.case_id

        self._event(
            FlowStage.INTAKE,
            "Intake completed",
            case_id=intake_result.case_id,
            exception_type=intake_result.exception_type,
            risk=intake_result.risk,
        )
        self._persist_snapshot()
        return intake_result

    @listen(intake)
    def retrieve_case_data(self, intake_result):
        self._set_stage(FlowStage.RETRIEVE_CASE_DATA, WorkflowStatus.RUNNING)
        self._event(FlowStage.RETRIEVE_CASE_DATA, "Starting reference data retrieval")

        case_context = self.retrieval_agent.run(intake_result)
        self.state.case_context = case_context
        
        self.state.memory_context = self.memory_service.build_memory_context(
            intake=self.state.intake_result,
            case_context=case_context,
        )

        
        self._event(
            FlowStage.RETRIEVE_CASE_DATA,
            "Memory context loaded",
            episodic_cases=len(self.state.memory_context.episodic_cases) if self.state.memory_context else 0,
            approval_history=len(self.state.memory_context.approval_history) if self.state.memory_context else 0,
        )

        self._event(
            FlowStage.RETRIEVE_CASE_DATA,
            "Reference data retrieval completed",
            retrieval_strength=case_context.retrieval_strength,
            data_conflicts=case_context.data_conflicts,
        )
        self._persist_snapshot()
        return case_context

    @listen(retrieve_case_data)
    def retrieve_policy_context(self, case_context):
        self._set_stage(FlowStage.RETRIEVE_POLICY_CONTEXT, WorkflowStatus.RUNNING)
        self._event(FlowStage.RETRIEVE_POLICY_CONTEXT, "Starting policy retrieval")

        rag_context = self.rag_agent.run(
            intake=self.state.intake_result,
            case_context=case_context,
        )
        self.state.rag_context = rag_context

        self._event(
            FlowStage.RETRIEVE_POLICY_CONTEXT,
            "Policy retrieval completed",
            retrieval_strength=rag_context.retrieval_strength,
            contradictions=rag_context.policy_contradictions,
        )
        self._persist_snapshot()
        return rag_context

    @listen(retrieve_policy_context)
    def infer_root_cause(self, rag_context):
        self._set_stage(FlowStage.INFER_ROOT_CAUSE, WorkflowStatus.RUNNING)
        self._event(FlowStage.INFER_ROOT_CAUSE, "Starting root cause assessment")

        root_cause = self.root_cause_agent.run(
            intake=self.state.intake_result,
            case_context=self.state.case_context,
            rag_context=rag_context,
        )
        self.state.root_cause = root_cause

        self._event(
            FlowStage.INFER_ROOT_CAUSE,
            "Root cause assessment completed",
            likely_root_cause=root_cause.likely_root_cause,
            confidence=root_cause.confidence,
        )
        self._persist_snapshot()
        return root_cause

    @listen(infer_root_cause)
    def recommend_action(self, root_cause):
        self._set_stage(FlowStage.RECOMMEND_ACTION, WorkflowStatus.RUNNING)
        self._event(FlowStage.RECOMMEND_ACTION, "Starting action recommendation")

        recommendation = self.recommendation_agent.run(
            intake=self.state.intake_result,
            case_context=self.state.case_context,
            rag_context=self.state.rag_context,
            root_cause=root_cause,
            memory_context=self.state.memory_context,
        )
        self.state.recommendation = recommendation

        self._event(
            FlowStage.RECOMMEND_ACTION,
            "Action recommendation completed",
            action_code=recommendation.action_code,
            confidence=recommendation.confidence,
        )
        self._persist_snapshot()
        return recommendation

    @listen(recommend_action)
    def check_approval_rules(self, recommendation):
        self._set_stage(FlowStage.CHECK_APPROVAL_RULES, WorkflowStatus.RUNNING)
        self._event(FlowStage.CHECK_APPROVAL_RULES, "Evaluating deterministic approval policy")

        approval_decision = self.hitl_agent.run(
            intake=self.state.intake_result,
            case_context=self.state.case_context,
            rag_context=self.state.rag_context,
            root_cause=self.state.root_cause,
            recommendation=recommendation,
        )
        self.state.approval_decision = approval_decision

        self._event(
            FlowStage.CHECK_APPROVAL_RULES,
            "Approval policy evaluation completed",
            status=approval_decision.status,
            requires_human_approval=approval_decision.requires_human_approval,
            route_to=approval_decision.route_to,
        )

        self.state.persisted_approval_ref = self.persistence.persist_approval_request(
            self.state,
            approval_decision,
        )
        self._persist_snapshot()
        return approval_decision

    @router(check_approval_rules)
    def approval_router(self, approval_decision):
        if approval_decision.requires_human_approval:
            return "request_human_approval"
        return "finalize_draft"

    @listen("request_human_approval")
    def request_human_approval(self):
        self._set_stage(FlowStage.REQUEST_HUMAN_APPROVAL, WorkflowStatus.PENDING_HUMAN_APPROVAL)
        self.state.reviewer_decision = ReviewerDecision.PENDING

        self._event(
            FlowStage.REQUEST_HUMAN_APPROVAL,
            "Case routed for human approval",
            reasons=self.state.approval_decision.reasons if self.state.approval_decision else [],
            route_to=self.state.approval_decision.route_to if self.state.approval_decision else "OPS_REVIEWER",
        )

        self._set_stage(FlowStage.PERSIST_AUDIT_TRAIL, WorkflowStatus.PENDING_HUMAN_APPROVAL)
        self._finalize_audit_and_persist()

        self.state.final_summary = self._build_final_summary()
        self._set_stage(FlowStage.RETURN_FINAL_SUMMARY, WorkflowStatus.PENDING_HUMAN_APPROVAL)
        self._persist_snapshot()
        return self.state.final_summary

    @listen("finalize_draft")
    def finalize_draft(self):
        self._set_stage(FlowStage.FINALIZE_DRAFT, WorkflowStatus.RUNNING)
        self._event(FlowStage.FINALIZE_DRAFT, "Auto-approved path selected, finalizing case draft")

        if self.state.approval_decision and self.state.approval_decision.status == "BLOCKED":
            self.state.workflow_status = WorkflowStatus.BLOCKED
        else:
            self.state.workflow_status = WorkflowStatus.COMPLETED

        self._set_stage(FlowStage.PERSIST_AUDIT_TRAIL, self.state.workflow_status)
        self._finalize_audit_and_persist()

        self.state.completed_at_utc = utc_now()
        self.state.final_summary = self._build_final_summary()

        self._set_stage(FlowStage.RETURN_FINAL_SUMMARY, self.state.workflow_status)
        self._event(
            FlowStage.RETURN_FINAL_SUMMARY,
            "Workflow completed",
            workflow_status=self.state.workflow_status.value,
        )
        self._persist_snapshot()
        return self.state.final_summary


class TradeExceptionResolutionFlowRunner:
    """
    Public service wrapper used by API/UI.
    """

    def __init__(self):
        self.persistence = WorkflowPersistenceService()

    def run(self, payload: Dict[str, Any]) -> FinalCaseSummary:
        """
        Execute the full workflow end-to-end for a new case.
        
        Returns the final case summary after all stages complete or HITL is triggered.
        """
        flow = TradeExceptionResolutionFlow()
        flow.state.request_payload = payload
        flow.state.workflow_status = WorkflowStatus.NOT_STARTED
        flow.state.started_at_utc = utc_now()
        flow._persist_snapshot()
        
        try:
            result = flow.kickoff()
            # kickoff() returns the result of the final listened method (FinalCaseSummary)
            if isinstance(result, FinalCaseSummary):
                return result
            # Fallback to state's final_summary if kickoff returns something else
            if flow.state.final_summary:
                return flow.state.final_summary
            # If neither exists, this is an error state
            raise RuntimeError("Flow execution completed but no final summary was produced")
        except Exception as exc:
            flow.state.errors.append(f"Flow execution failed: {str(exc)}")
            flow.state.workflow_status = WorkflowStatus.FAILED
            flow._persist_snapshot()
            raise

    def resume_after_human_review(
        self,
        case_id: str,
        request: HumanApprovalRequest,
    ) -> FinalCaseSummary:
        """
        Resume a workflow after human reviewer provides approval/rejection decision.
        
        Updates the approval decision, finalizes audit, and returns final summary.
        """
        state = self.persistence.apply_human_decision(case_id=case_id, request=request)
        if state is None:
            raise ValueError(f"No persisted flow state found for case_id={case_id}")

        # Update workflow status and approval decision based on reviewer decision
        if request.approved:
            state.workflow_status = WorkflowStatus.COMPLETED
            if state.approval_decision is not None:
                state.approval_decision.status = "AUTO_APPROVED"
                state.approval_decision.requires_human_approval = False
                state.approval_decision.reasons = [
                    *state.approval_decision.reasons,
                    f"Human reviewer {request.reviewer_name} approved case",
                ]
        else:
            state.workflow_status = WorkflowStatus.BLOCKED
            if state.approval_decision is not None:
                state.approval_decision.status = "BLOCKED"
                state.approval_decision.reasons = [
                    *state.approval_decision.reasons,
                    f"Human reviewer {request.reviewer_name} rejected case",
                ]

        # Create a flow instance to finalize audit with updated state
        flow = TradeExceptionResolutionFlow()
        flow.state = state
        flow.state.current_stage = FlowStage.PERSIST_AUDIT_TRAIL
        flow.state.updated_at_utc = utc_now()
        
        try:
            flow._finalize_audit_and_persist()
            flow.state.completed_at_utc = utc_now()
            flow.state.current_stage = FlowStage.RETURN_FINAL_SUMMARY
            flow.state.final_summary = flow._build_final_summary()
            flow._persist_snapshot()
            
            return flow.state.final_summary
        except Exception as exc:
            flow.state.errors.append(f"HITL resume failed: {str(exc)}")
            flow.state.workflow_status = WorkflowStatus.FAILED
            flow._persist_snapshot()
            raise