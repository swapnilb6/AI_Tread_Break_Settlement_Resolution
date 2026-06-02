from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import (
    CounterpartyModel,
    MarketCalendarModel,
    ResolutionHistoryModel,
    SettlementModel,
    SSIMasterModel,
    TradeModel,
)


class ReferenceDataRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_trade(self, trade_id: str) -> TradeModel | None:
        stmt = select(TradeModel).where(TradeModel.trade_id == trade_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_settlement(self, trade_id: str) -> SettlementModel | None:
        stmt = select(SettlementModel).where(SettlementModel.trade_id == trade_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_ssi_by_counterparty(self, counterparty_id: str) -> list[SSIMasterModel]:
        stmt = (
            select(SSIMasterModel)
            .where(SSIMasterModel.counterparty_id == counterparty_id)
            .order_by(SSIMasterModel.market, SSIMasterModel.currency, SSIMasterModel.ssi_id)
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_counterparty(self, counterparty_id: str) -> CounterpartyModel | None:
        stmt = select(CounterpartyModel).where(CounterpartyModel.counterparty_id == counterparty_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_calendar_day(self, market: str, calendar_date: str) -> MarketCalendarModel | None:
        stmt = select(MarketCalendarModel).where(
            MarketCalendarModel.market == market,
            MarketCalendarModel.calendar_date == calendar_date,
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_similar_history(self, signature: str, limit: int = 5) -> list[ResolutionHistoryModel]:
        stmt = select(ResolutionHistoryModel)
        rows = list(self.db.execute(stmt).scalars().all())

        target_parts = signature.split("|")

        def score(row: ResolutionHistoryModel) -> int:
            row_parts = row.exception_signature.split("|")
            return sum(1 for left, right in zip(target_parts, row_parts) if left == right)

        ranked = sorted(rows, key=score, reverse=True)
        filtered = [row for row in ranked if score(row) > 0]
        return filtered[:limit]