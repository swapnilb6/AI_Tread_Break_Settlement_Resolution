# app/api/routers/cases.py
from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from app.orchestration.flow import TradeExceptionResolutionFlowRunner
from app.schemas.flow_state import (
    CaseResolutionFlowState,
    FinalCaseSummary,
    HumanApprovalRequest,
)
from app.services.workflow_persistence_service import WorkflowPersistenceService

router = APIRouter(prefix="/cases", tags=["cases"])

flow_runner = TradeExceptionResolutionFlowRunner()
persistence_service = WorkflowPersistenceService()


@router.post("/workflow/run", response_model=FinalCaseSummary)
def run_case_workflow(payload: Dict[str, Any]) -> FinalCaseSummary:
    try:
        return flow_runner.run(payload)
    except Exception as exc:
        import traceback
        raise HTTPException(
            status_code=500,
            detail=f"Workflow execution failed: {type(exc).__name__}: {exc}"
        )


@router.post("/{case_id}/approval", response_model=FinalCaseSummary)
def submit_human_approval(case_id: str, request: HumanApprovalRequest) -> FinalCaseSummary:
    try:
        return flow_runner.resume_after_human_review(case_id=case_id, request=request)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Approval processing failed: {exc}")


@router.get("/{case_id}/state", response_model=CaseResolutionFlowState)
def get_case_state(case_id: str) -> CaseResolutionFlowState:
    try:
        state = persistence_service.load_flow_snapshot(case_id=case_id)
        if state is None:
            raise HTTPException(status_code=404, detail=f"No persisted flow state found for case_id={case_id}")
        return state
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to load case state: {exc}")