# app/api/routers/cases.py
from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from app.orchestration.flow import TradeExceptionResolutionFlowRunner
from app.schemas.flow_state import FinalCaseSummary, HumanApprovalRequest

router = APIRouter(prefix="/cases", tags=["cases"])

flow_runner = TradeExceptionResolutionFlowRunner()


@router.post("/workflow/run", response_model=FinalCaseSummary)
def run_case_workflow(payload: Dict[str, Any]) -> FinalCaseSummary:
    try:
        return flow_runner.run(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {exc}")


@router.post("/{case_id}/approval", response_model=FinalCaseSummary)
def submit_human_approval(case_id: str, request: HumanApprovalRequest) -> FinalCaseSummary:
    try:
        return flow_runner.resume_after_human_review(case_id=case_id, request=request)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Approval processing failed: {exc}")
