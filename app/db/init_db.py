from app.db.base import Base
from app.db.models import (
    CounterpartyModel,
    MarketCalendarModel,
    OpsNoteModel,
    ResolutionHistoryModel,
    SettlementModel,
    SSIMasterModel,
    TradeExceptionModel,
    TradeModel,
)
from app.db.session import engine


def init_db() -> None:
    Base.metadata.create_all(bind=engine)