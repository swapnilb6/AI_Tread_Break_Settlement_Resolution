from app.agents.audit_agent import AuditAgentService
from app.agents.hitl_agent import HITLAgentService
from app.agents.intake_agent import IntakeAgentService
from app.agents.policy_rag_agent import PolicyRAGAgentService
from app.agents.recommendation_agent import RecommendationAgentService
from app.agents.retrieval_agent import RetrievalAgentService
from app.agents.root_cause_agent import RootCauseAgentService
from app.schemas.agent_outputs import (
    AuditRecord,
    CaseContext,
    IntakeResult,
    RAGContext,
    RootCauseAssessment,
    ActionRecommendation,
    ApprovalDecision,
)


class ExceptionResolutionFlow:
    """
    Phase 5 orchestration flow for Capital Markets Trade Break & Settlement Exception Resolution.
    
    Orchestrates 7 agents in sequence:
    1. Intake Agent - Classifies exception and extracts initial data
    2. Retrieval Agent - Fetches reference data
    3. Policy/RAG Agent - Retrieves policy evidence
    4. Root Cause Agent - Assesses likely root cause
    5. Recommendation Agent - Recommends next action
    6. HITL Agent - Applies deterministic approval policy
    7. Audit Agent - Assembles final audit record
    
    Each agent is called standalone with its run() method.
    All outputs are validated against strict Pydantic schemas.
    """

    def __init__(self):
        self.intake_service = IntakeAgentService()
        self.retrieval_service = RetrievalAgentService()
        self.rag_service = PolicyRAGAgentService()
        self.root_cause_service = RootCauseAgentService()
        self.recommendation_service = RecommendationAgentService()
        self.hitl_service = HITLAgentService()
        self.audit_service = AuditAgentService()

    def run(self, intake_payload: dict) -> AuditRecord:
        """
        Execute the full exception resolution workflow.
        
        Args:
            intake_payload: Dictionary with exception data (trade_id, summary, etc.)
            
        Returns:
            AuditRecord with complete case analysis and decision
        """
        # Step 1: Intake - Classify exception and extract identifiers
        intake: IntakeResult = self.intake_service.run(intake_payload)
        
        # Step 2: Retrieval - Fetch all reference data
        case_context: CaseContext = self.retrieval_service.run(intake)
        
        # Step 3: RAG - Retrieve policy evidence
        rag_context: RAGContext = self.rag_service.run(intake, case_context)
        
        # Step 4: Root Cause - Assess likely operational root cause
        root_cause: RootCauseAssessment = self.root_cause_service.run(
            intake, case_context, rag_context
        )
        
        # Step 5: Recommendation - Recommend next action
        recommendation: ActionRecommendation = self.recommendation_service.run(
            intake, case_context, rag_context, root_cause
        )
        
        # Step 6: HITL - Apply approval policy and determine routing
        approval: ApprovalDecision = self.hitl_service.run(
            intake, case_context, rag_context, root_cause, recommendation
        )
        
        # Step 7: Audit - Assemble final audit record
        audit_record: AuditRecord = self.audit_service.run(
            intake, case_context, rag_context, root_cause, recommendation, approval
        )
        
        return audit_record

    def run_steps_independently(self, intake_payload: dict) -> dict:
        """
        Run each step independently and return all results.
        Useful for debugging and testing individual agents.
        """
        intake = self.intake_service.run(intake_payload)
        case_context = self.retrieval_service.run(intake)
        rag_context = self.rag_service.run(intake, case_context)
        root_cause = self.root_cause_service.run(intake, case_context, rag_context)
        recommendation = self.recommendation_service.run(intake, case_context, rag_context, root_cause)
        approval = self.hitl_service.run(intake, case_context, rag_context, root_cause, recommendation)
        audit_record = self.audit_service.run(intake, case_context, rag_context, root_cause, recommendation, approval)
        
        return {
            "intake": intake,
            "case_context": case_context,
            "rag_context": rag_context,
            "root_cause": root_cause,
            "recommendation": recommendation,
            "approval": approval,
            "audit_record": audit_record,
        }