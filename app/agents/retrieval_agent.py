# app/agents/retrieval_agent.py
from __future__ import annotations

from crewai import Task

from app.agents.base import build_crewai_agent
from app.schemas.agent_outputs import CaseContext, IntakeResult
from app.tools.reference_data_tools import (
    build_reference_evidence,
    get_calendar_record,
    get_counterparty_record,
    get_settlement_record,
    get_similar_history,
    get_ssi_record,
    get_trade_record,
)


class RetrievalAgentService:
    def run(self, intake: IntakeResult) -> CaseContext:
        """
        Retrieve all reference data needed to build case context.
        """
        tool_trace = []
        trade = None
        settlement = None
        ssi = None
        counterparty = None
        calendar = None
        similar_cases = []

        # Get trade record
        if intake.trade_id:
            trade, trade_trace = get_trade_record(intake.trade_id)
            tool_trace.append(trade_trace)

        # Get settlement record
        if intake.trade_id:
            settlement, settlement_trace = get_settlement_record(intake.trade_id)
            tool_trace.append(settlement_trace)

        # Get SSI records
        if intake.counterparty_id:
            ssi, ssi_trace = get_ssi_record(intake.counterparty_id)
            tool_trace.append(ssi_trace)

        # Get counterparty record
        if intake.counterparty_id:
            counterparty, cp_trace = get_counterparty_record(intake.counterparty_id)
            tool_trace.append(cp_trace)

        # Get market calendar record
        market_date = None
        if settlement and settlement.get("intended_settlement_date"):
            market_date = str(settlement["intended_settlement_date"])
        elif trade and trade.get("settlement_date"):
            market_date = str(trade["settlement_date"])

        if intake.market and market_date:
            calendar, calendar_trace = get_calendar_record(intake.market, market_date)
            tool_trace.append(calendar_trace)

        # Get similar historical cases
        signature = f"{intake.exception_type}|{intake.counterparty_id or ''}|{intake.market or ''}"
        similar_cases, history_trace = get_similar_history(signature)
        tool_trace.append(history_trace)

        # Detect data conflicts
        data_conflicts = []
        if trade and settlement:
            if trade.get("quantity") != settlement.get("quantity"):
                data_conflicts.append("trade quantity differs from settlement quantity")
            if trade.get("price") != settlement.get("price"):
                data_conflicts.append("trade price differs from settlement price")

        if ssi and settlement:
            # SSI is a list, settlement is a dict
            ssi_list = ssi if isinstance(ssi, list) else [ssi]
            for ssi_record in ssi_list:
                if ssi_record.get("account_no") != settlement.get("ssi_id"):
                    data_conflicts.append("SSI account does not match settlement SSI")

        # Assess evidence completeness
        evidence_complete = all(
            [
                intake.trade_id is not None,
                trade is not None,
                settlement is not None,
                intake.counterparty_id is not None,
                counterparty is not None,
            ]
        )

        # Calculate retrieval strength
        successful_calls = sum(1 for t in tool_trace if t.status == "SUCCESS")
        retrieval_strength = round(successful_calls / max(len(tool_trace), 1), 2)

        # Build evidence references
        evidence_refs = build_reference_evidence(
            trade=trade,
            settlement=settlement,
            ssi=ssi,
            counterparty=counterparty,
            calendar=calendar,
            similar_cases=similar_cases,
        )

        return CaseContext(
            case_id=intake.case_id,
            trade=trade,
            settlement=settlement,
            ssi=ssi,
            counterparty=counterparty,
            market_calendar=calendar,
            similar_cases=similar_cases,
            ops_notes=[],
            evidence_complete=evidence_complete,
            data_conflicts=data_conflicts,
            retrieval_strength=retrieval_strength,
            evidence_refs=evidence_refs,
            tool_trace=tool_trace,
        )

    @staticmethod
    def build_agent():
        return build_crewai_agent(
            role="Reference Data Retrieval Specialist",
            goal="Retrieve all reference data needed for case analysis",
            backstory="Expert in capital markets reference data, settlement operations, counterparty data, and trade reconciliation.",
        )

    @staticmethod
    def build_task(intake: IntakeResult, agent=None) -> Task:
        agent = agent or RetrievalAgentService.build_agent()
        return Task(
            description=(
                "Retrieve all reference data for the current case using the trade_id and counterparty_id. "
                "Return a valid CaseContext with all retrieved data and evidence references."
            ),
            expected_output="A valid CaseContext object.",
            output_pydantic=CaseContext,
            agent=agent,
        )
            similar_cases=similar_cases,
        )

        return CaseContext(
            case_id=intake.case_id,
            trade=trade,
            settlement=settlement,
            ssi=ssi,
            counterparty=counterparty,
            market_calendar=calendar,
            similar_cases=similar_cases,
            ops_notes=[],
            evidence_complete=evidence_complete,
            data_conflicts=data_conflicts,
            retrieval_strength=retrieval_strength,
            evidence_refs=evidence_refs,
            tool_trace=tool_trace,
        )

    @staticmethod
    def build_agent():
        return build_crewai_agent(
            role="Reference Data Retrieval Specialist",
            goal="Retrieve relevant reference data and historical cases for the active exception",
            backstory="Expert in trade capture, settlement records, SSI master, market calendars, and historical exception resolution context.",
        )

    @staticmethod
    def build_task(intake: IntakeResult, agent=None) -> Task:
        agent = agent or RetrievalAgentService.build_agent()
        return Task(
            description=(
                "Retrieve trade, settlement, SSI, counterparty, calendar, and similar historical cases "
                f"for case_id={intake.case_id}, trade_id={intake.trade_id}, counterparty_id={intake.counterparty_id}, "
                f"exception_type={intake.exception_type}, market={intake.market}."
            ),
            expected_output="A valid CaseContext object.",
            output_pydantic=CaseContext,
            agent=agent,
        )