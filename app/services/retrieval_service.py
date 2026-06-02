from app.repositories.reference_data_repo import ReferenceDataRepository
from app.schemas.reference_data import (
    CounterpartyResponse,
    MarketCalendarResponse,
    SettlementResponse,
    SimilarHistoryResponse,
    SSIResponse,
    TradeResponse,
)


class RetrievalService:
    def __init__(self, repo: ReferenceDataRepository):
        self.repo = repo

    def get_trade(self, trade_id: str) -> TradeResponse | None:
        row = self.repo.get_trade(trade_id)
        if not row:
            return None

        return TradeResponse(
            trade_id=row.trade_id,
            trade_date=row.trade_date,
            book=row.book,
            trader=row.trader,
            instrument=row.instrument,
            side=row.side,
            quantity=row.quantity,
            price=row.price,
            counterparty_id=row.counterparty_id,
            account=row.account,
            market=row.market,
            currency=row.currency,
            settlement_date=row.settlement_date,
            isin=row.isin,
            booking_timestamp=row.booking_timestamp,
        )

    def get_settlement(self, trade_id: str) -> SettlementResponse | None:
        row = self.repo.get_settlement(trade_id)
        if not row:
            return None

        return SettlementResponse(
            trade_id=row.trade_id,
            settlement_status=row.settlement_status,
            instruction_status=row.instruction_status,
            ssi_id=row.ssi_id,
            custodian=row.custodian,
            depository=row.depository,
            fail_reason_code=row.fail_reason_code,
            actual_settlement_date=row.actual_settlement_date,
            intended_settlement_date=row.intended_settlement_date,
        )

    def get_ssi(self, counterparty_id: str) -> list[SSIResponse]:
        rows = self.repo.get_ssi_by_counterparty(counterparty_id)
        return [
            SSIResponse(
                ssi_id=row.ssi_id,
                counterparty_id=row.counterparty_id,
                market=row.market,
                currency=row.currency,
                account_no=row.account_no,
                bic=row.bic,
                custodian=row.custodian,
                effective_from=row.effective_from,
                effective_to=row.effective_to,
                active_flag=row.active_flag,
            )
            for row in rows
        ]

    def get_counterparty(self, counterparty_id: str) -> CounterpartyResponse | None:
        row = self.repo.get_counterparty(counterparty_id)
        if not row:
            return None

        return CounterpartyResponse(
            counterparty_id=row.counterparty_id,
            counterparty_name=row.counterparty_name,
            lei=row.lei,
            bic=row.bic,
            region=row.region,
            default_market=row.default_market,
            risk_rating=row.risk_rating,
            active_flag=row.active_flag,
        )

    def get_calendar_day(self, market: str, calendar_date: str) -> MarketCalendarResponse | None:
        row = self.repo.get_calendar_day(market, calendar_date)
        if not row:
            return None

        return MarketCalendarResponse(
            market=row.market,
            calendar_date=row.calendar_date,
            is_business_day=row.is_business_day,
            holiday_name=row.holiday_name,
        )

    def get_similar_history(self, signature: str, limit: int = 5) -> list[SimilarHistoryResponse]:
        rows = self.repo.get_similar_history(signature=signature, limit=limit)
        target_parts = signature.split("|")

        def score(signature_text: str) -> int:
            parts = signature_text.split("|")
            return sum(1 for left, right in zip(target_parts, parts) if left == right)

        return [
            SimilarHistoryResponse(
                case_id=row.case_id,
                exception_signature=row.exception_signature,
                root_cause=row.root_cause,
                final_action=row.final_action,
                human_override_flag=row.human_override_flag,
                agent_confidence=row.agent_confidence,
                resolved_by=row.resolved_by,
                resolution_time_hours=row.resolution_time_hours,
                outcome=row.outcome,
                similarity_score=score(row.exception_signature),
            )
            for row in rows
        ]