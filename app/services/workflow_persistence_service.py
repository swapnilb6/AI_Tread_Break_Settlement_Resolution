# app/services/workflow_persistence_service.py
from __future__ import annotations

import inspect as pyinspect
from typing import Any, Dict, Optional, Type

from sqlalchemy.orm import Session

from app.db import models as db_models
from app.db.session import SessionLocal
from app.schemas.agent_outputs import ApprovalDecision, AuditRecord
from app.schemas.flow_state import (
    CaseResolutionFlowState,
    HumanApprovalRequest,
    ReviewerDecision,
    WorkflowStatus,
)


class WorkflowPersistenceService:
    """
    Patch-friendly persistence adapter.
    It tries to reuse existing ORM models by introspecting app.db.models
    and mapping available columns dynamically.
    """

    CASE_TABLE_HINTS = ("case", "workflow", "run")
    APPROVAL_TABLE_HINTS = ("approval", "review")
    AUDIT_TABLE_HINTS = ("audit", "trail", "log")

    def _iter_model_classes(self):
        for _, obj in pyinspect.getmembers(db_models, pyinspect.isclass):
            if hasattr(obj, "__tablename__") and hasattr(obj, "__table__"):
                yield obj

    def _find_model_by_hints(self, hints: tuple[str, ...]) -> Optional[Type]:
        for model_cls in self._iter_model_classes():
            table_name = str(getattr(model_cls, "__tablename__", "")).lower()
            if any(hint in table_name for hint in hints):
                return model_cls
        return None

    @staticmethod
    def _columns(model_cls: Type) -> set[str]:
        return {column.name for column in model_cls.__table__.columns}

    @staticmethod
    def _pick_first(cols: set[str], candidates: list[str]) -> Optional[str]:
        for candidate in candidates:
            if candidate in cols:
                return candidate
        return None

    def _upsert(
        self,
        session: Session,
        model_cls: Type,
        key_field: str,
        key_value: Any,
        values: Dict[str, Any],
    ) -> Any:
        instance = session.query(model_cls).filter(getattr(model_cls, key_field) == key_value).one_or_none()
        if instance is None:
            instance = model_cls(**{key_field: key_value})
            session.add(instance)

        for field_name, field_value in values.items():
            if hasattr(instance, field_name):
                setattr(instance, field_name, field_value)

        session.commit()
        session.refresh(instance)
        return instance

    def persist_flow_snapshot(self, state: CaseResolutionFlowState) -> Optional[str]:
        session = SessionLocal()
        try:
            model_cls = self._find_model_by_hints(self.CASE_TABLE_HINTS)
            if model_cls is None:
                return None

            cols = self._columns(model_cls)
            key_field = self._pick_first(cols, ["case_id", "id", "flow_id"])
            if key_field is None:
                return None

            snapshot_field = self._pick_first(
                cols,
                [
                    "state_json",
                    "snapshot_json",
                    "payload_json",
                    "case_payload",
                    "case_snapshot",
                    "details_json",
                    "metadata_json",
                ],
            )
            status_field = self._pick_first(cols, ["status", "case_status", "workflow_status"])
            stage_field = self._pick_first(cols, ["current_stage", "stage"])
            flow_id_field = self._pick_first(cols, ["flow_id"])
            started_field = self._pick_first(cols, ["started_at_utc", "created_at", "started_at"])
            updated_field = self._pick_first(cols, ["updated_at_utc", "updated_at", "modified_at"])
            case_id_field = self._pick_first(cols, ["case_id"])

            values: Dict[str, Any] = {}
            if snapshot_field:
                values[snapshot_field] = state.model_dump(mode="json")
            if status_field:
                values[status_field] = state.workflow_status.value
            if stage_field:
                values[stage_field] = state.current_stage.value
            if flow_id_field:
                values[flow_id_field] = state.flow_id
            if started_field:
                values[started_field] = state.started_at_utc
            if updated_field:
                values[updated_field] = state.updated_at_utc
            if case_id_field and key_field != "case_id":
                values[case_id_field] = state.case_id or state.flow_id

            natural_key_value = state.case_id or state.flow_id
            row = self._upsert(
                session=session,
                model_cls=model_cls,
                key_field=key_field,
                key_value=natural_key_value,
                values=values,
            )

            return str(getattr(row, key_field))
        finally:
            session.close()

    def persist_approval_request(
        self,
        state: CaseResolutionFlowState,
        approval: ApprovalDecision,
    ) -> Optional[str]:
        session = SessionLocal()
        try:
            model_cls = self._find_model_by_hints(self.APPROVAL_TABLE_HINTS)
            if model_cls is None:
                return None

            cols = self._columns(model_cls)
            key_field = self._pick_first(cols, ["case_id", "id", "approval_id"])
            if key_field is None:
                return None

            values: Dict[str, Any] = {}
            mapping = {
                "case_id": state.case_id,
                "status": approval.status,
                "route_to": approval.route_to,
                "requires_human_approval": approval.requires_human_approval,
                "reasons": approval.reasons,
                "policy_checks": [check.model_dump(mode="json") for check in approval.policy_checks],
                "reviewer_decision": state.reviewer_decision.value,
                "reviewer_name": state.reviewer_name,
                "reviewer_comments": state.reviewer_comments,
                "exception_type": state.intake_result.exception_type if state.intake_result else None,
                "action_code": state.recommendation.action_code if state.recommendation else None,

            }

            for field_name, field_value in mapping.items():
                if field_name in cols:
                    values[field_name] = field_value

            natural_key_value = state.case_id or approval.case_id
            row = self._upsert(
                session=session,
                model_cls=model_cls,
                key_field=key_field,
                key_value=natural_key_value,
                values=values,
            )
            return str(getattr(row, key_field))
        finally:
            session.close()

    def persist_audit_record(self, audit_record: AuditRecord) -> Optional[str]:
        session = SessionLocal()
        try:
            model_cls = self._find_model_by_hints(self.AUDIT_TABLE_HINTS)
            if model_cls is None:
                return None

            cols = self._columns(model_cls)
            key_field = self._pick_first(cols, ["case_id", "id", "audit_id"])
            if key_field is None:
                return None

            values: Dict[str, Any] = {}
            mapping = {
                "case_id": audit_record.case_id,
                "status": audit_record.case_status,
                "case_status": audit_record.case_status,
                "generated_at_utc": audit_record.generated_at_utc,
                "audit_version": audit_record.audit_version,
                "audit_json": audit_record.model_dump(mode="json"),
                "payload_json": audit_record.model_dump(mode="json"),
                "details_json": audit_record.model_dump(mode="json"),
            }

            for field_name, field_value in mapping.items():
                if field_name in cols:
                    values[field_name] = field_value

            natural_key_value = audit_record.case_id
            row = self._upsert(
                session=session,
                model_cls=model_cls,
                key_field=key_field,
                key_value=natural_key_value,
                values=values,
            )
            return str(getattr(row, key_field))
        finally:
            session.close()

    def load_flow_snapshot(self, case_id: str) -> Optional[CaseResolutionFlowState]:
        session = SessionLocal()
        try:
            model_cls = self._find_model_by_hints(self.CASE_TABLE_HINTS)
            if model_cls is None:
                return None

            cols = self._columns(model_cls)
            key_field = self._pick_first(cols, ["case_id", "id", "flow_id"])
            snapshot_field = self._pick_first(
                cols,
                [
                    "state_json",
                    "snapshot_json",
                    "payload_json",
                    "case_payload",
                    "case_snapshot",
                    "details_json",
                    "metadata_json",
                ],
            )
            if key_field is None or snapshot_field is None:
                return None

            row = session.query(model_cls).filter(getattr(model_cls, key_field) == case_id).one_or_none()
            if row is None:
                return None

            snapshot = getattr(row, snapshot_field, None)
            if not snapshot:
                return None

            return CaseResolutionFlowState.model_validate(snapshot)
        finally:
            session.close()

    def apply_human_decision(
        self,
        case_id: str,
        request: HumanApprovalRequest,
    ) -> Optional[CaseResolutionFlowState]:
        state = self.load_flow_snapshot(case_id=case_id)
        if state is None:
            return None

        state.reviewer_name = request.reviewer_name
        state.reviewer_comments = request.reviewer_comments
        state.reviewer_decision = (
            ReviewerDecision.APPROVED if request.approved else ReviewerDecision.REJECTED
        )

        if request.approved:
            state.workflow_status = WorkflowStatus.COMPLETED
        else:
            state.workflow_status = WorkflowStatus.BLOCKED

        return state