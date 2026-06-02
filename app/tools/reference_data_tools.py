# app/tools/reference_data_tools.py
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from app.db.session import SessionLocal
from app.repositories.reference_data_repo import ReferenceDataRepository
from app.schemas.agent_outputs import DataEvidenceRef, ToolExecutionRecord
from app.services.retrieval_service import RetrievalService


def _safe_summary(value: Any) -> str:
    if value is None:
        return "no result"
    if isinstance(value, list):
        return f"{len(value)} record(s)"
    if isinstance(value, dict):
        return f"dict keys={list(value.keys())[:8]}"
    return str(type(value).__name__)


def _normalize_model(result: Any) -> Optional[Dict[str, Any]]:
    if result is None:
        return None
    if isinstance(result, dict):
        return result
    if hasattr(result, "model_dump"):
        return result.model_dump()
    if hasattr(result, "__dict__"):
        return {k: v for k, v in vars(result).items() if not k.startswith("_")}
    return {"value": str(result)}


def get_trade_record(trade_id: str) -> Tuple[Optional[Dict[str, Any]], ToolExecutionRecord]:
    session = SessionLocal()
    try:
        repo = ReferenceDataRepository(session)
        service = RetrievalService(repo)
        result = service.get_trade(trade_id)
        data = _normalize_model(result)
        return data, ToolExecutionRecord(
            tool_name="get_trade_record",
            arguments={"trade_id": trade_id},
            status="SUCCESS",
            record_count=1 if data else 0,
            output_summary=_safe_summary(data),
        )
    except Exception as exc:
        return None, ToolExecutionRecord(
            tool_name="get_trade_record",
            arguments={"trade_id": trade_id},
            status="ERROR",
            error_message=str(exc),
        )
    finally:
        session.close()


def get_settlement_record(trade_id: str) -> Tuple[Optional[Dict[str, Any]], ToolExecutionRecord]:
    session = SessionLocal()
    try:
        repo = ReferenceDataRepository(session)
        service = RetrievalService(repo)
        result = service.get_settlement(trade_id)
        data = _normalize_model(result)
        return data, ToolExecutionRecord(
            tool_name="get_settlement_record",
            arguments={"trade_id": trade_id},
            status="SUCCESS",
            record_count=1 if data else 0,
            output_summary=_safe_summary(data),
        )
    except Exception as exc:
        return None, ToolExecutionRecord(
            tool_name="get_settlement_record",
            arguments={"trade_id": trade_id},
            status="ERROR",
            error_message=str(exc),
        )
    finally:
        session.close()


def get_ssi_record(counterparty_id: str) -> Tuple[Optional[List[Dict[str, Any]]], ToolExecutionRecord]:
    session = SessionLocal()
    try:
        repo = ReferenceDataRepository(session)
        service = RetrievalService(repo)
        result = service.get_ssi(counterparty_id)
        data = [_normalize_model(r) for r in (result or [])]
        return data, ToolExecutionRecord(
            tool_name="get_ssi_record",
            arguments={"counterparty_id": counterparty_id},
            status="SUCCESS",
            record_count=len(data),
            output_summary=_safe_summary(data),
        )
    except Exception as exc:
        return None, ToolExecutionRecord(
            tool_name="get_ssi_record",
            arguments={"counterparty_id": counterparty_id},
            status="ERROR",
            error_message=str(exc),
        )
    finally:
        session.close()


def get_counterparty_record(counterparty_id: str) -> Tuple[Optional[Dict[str, Any]], ToolExecutionRecord]:
    session = SessionLocal()
    try:
        repo = ReferenceDataRepository(session)
        service = RetrievalService(repo)
        result = service.get_counterparty(counterparty_id)
        data = _normalize_model(result)
        return data, ToolExecutionRecord(
            tool_name="get_counterparty_record",
            arguments={"counterparty_id": counterparty_id},
            status="SUCCESS",
            record_count=1 if data else 0,
            output_summary=_safe_summary(data),
        )
    except Exception as exc:
        return None, ToolExecutionRecord(
            tool_name="get_counterparty_record",
            arguments={"counterparty_id": counterparty_id},
            status="ERROR",
            error_message=str(exc),
        )
    finally:
        session.close()


def get_calendar_record(market: str, calendar_date: str) -> Tuple[Optional[Dict[str, Any]], ToolExecutionRecord]:
    session = SessionLocal()
    try:
        repo = ReferenceDataRepository(session)
        service = RetrievalService(repo)
        result = service.get_calendar_day(market, calendar_date)
        data = _normalize_model(result)
        return data, ToolExecutionRecord(
            tool_name="get_calendar_record",
            arguments={"market": market, "calendar_date": calendar_date},
            status="SUCCESS",
            record_count=1 if data else 0,
            output_summary=_safe_summary(data),
        )
    except Exception as exc:
        return None, ToolExecutionRecord(
            tool_name="get_calendar_record",
            arguments={"market": market, "calendar_date": calendar_date},
            status="ERROR",
            error_message=str(exc),
        )
    finally:
        session.close()


def get_similar_history(signature: str) -> Tuple[List[Dict[str, Any]], ToolExecutionRecord]:
    session = SessionLocal()
    try:
        repo = ReferenceDataRepository(session)
        service = RetrievalService(repo)
        result = service.get_similar_history(signature)
        if result is None:
            data = []
        elif isinstance(result, list):
            data = [_normalize_model(r) for r in result]
        else:
            data = [_normalize_model(result)]

        return data, ToolExecutionRecord(
            tool_name="get_similar_history",
            arguments={"signature": signature},
            status="SUCCESS",
            record_count=len(data),
            output_summary=f"{len(data)} similar historical case(s)",
        )
    except Exception as exc:
        return [], ToolExecutionRecord(
            tool_name="get_similar_history",
            arguments={"signature": signature},
            status="ERROR",
            error_message=str(exc),
        )
    finally:
        session.close()


def build_reference_evidence(
    trade: Optional[Dict[str, Any]],
    settlement: Optional[Dict[str, Any]],
    ssi: Optional[List[Dict[str, Any]]],
    counterparty: Optional[Dict[str, Any]],
    calendar: Optional[Dict[str, Any]],
    similar_cases: List[Dict[str, Any]],
) -> List[DataEvidenceRef]:
    refs: List[DataEvidenceRef] = []

    if trade:
        refs.append(
            DataEvidenceRef(
                source_type="trade",
                source_id=str(trade.get("trade_id", "unknown_trade")),
                description="Trade record retrieved from reference store",
                fields_used=list(trade.keys())[:12],
            )
        )

    if settlement:
        refs.append(
            DataEvidenceRef(
                source_type="settlement",
                source_id=str(settlement.get("trade_id", "unknown_trade")),
                description="Settlement record retrieved from reference store",
                fields_used=list(settlement.keys())[:12],
            )
        )

    if ssi and len(ssi) > 0:
        ssi_ids = [s.get("ssi_id", "unknown") for s in (ssi if isinstance(ssi, list) else [ssi])]
        refs.append(
            DataEvidenceRef(
                source_type="ssi",
                source_id=",".join(ssi_ids[:3]),
                description=f"SSI records retrieved for counterparty ({len(ssi if isinstance(ssi, list) else [ssi])} record(s))",
                fields_used=list((ssi[0] if isinstance(ssi, list) else ssi).keys())[:12],
            )
        )

    if counterparty:
        refs.append(
            DataEvidenceRef(
                source_type="counterparty",
                source_id=str(counterparty.get("counterparty_id", "unknown_counterparty")),
                description="Counterparty record retrieved from reference store",
                fields_used=list(counterparty.keys())[:12],
            )
        )

    if calendar:
        refs.append(
            DataEvidenceRef(
                source_type="calendar",
                source_id=f"{calendar.get('market', 'unknown')}_{calendar.get('calendar_date', 'unknown')}",
                description="Market calendar record retrieved from reference store",
                fields_used=list(calendar.keys())[:12],
            )
        )

    if similar_cases:
        for idx, case in enumerate(similar_cases[:3]):
            refs.append(
                DataEvidenceRef(
                    source_type="history",
                    source_id=str(case.get("case_id", f"unknown_case_{idx}")),
                    description=f"Similar historical case: {case.get('root_cause', 'unknown root cause')}",
                    fields_used=list(case.keys())[:12],
                )
            )

    return refs
                description="SSI master record retrieved from reference store",
                fields_used=list(ssi.keys())[:12],
            )
        )

    if counterparty:
        refs.append(
            DataEvidenceRef(
                source_type="counterparty",
                source_id=str(counterparty.get("counterparty_id", "unknown_counterparty")),
                description="Counterparty master retrieved from reference store",
                fields_used=list(counterparty.keys())[:12],
            )
        )

    if calendar:
        refs.append(
            DataEvidenceRef(
                source_type="calendar",
                source_id=f"{calendar.get('market', 'unknown')}:{calendar.get('date', 'unknown')}",
                description="Market calendar record retrieved from reference store",
                fields_used=list(calendar.keys())[:12],
            )
        )

    for idx, case in enumerate(similar_cases, start=1):
        refs.append(
            DataEvidenceRef(
                source_type="history",
                source_id=str(case.get("case_id", f"history_{idx}")),
                description="Similar resolved historical case retrieved from Postgres",
                fields_used=list(case.keys())[:12],
            )
        )

    return refs
