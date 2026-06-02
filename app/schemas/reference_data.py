from pydantic import Field

from app.schemas.common import StrictBaseModel


class TradeResponse(StrictBaseModel):
    trade_id: str
    trade_date: str
    book: str
    trader: str
    instrument: str
    side: str
    quantity: float
    price: float
    counterparty_id: str
    account: str | None = None
    market: str
    currency: str
    settlement_date: str
    isin: str | None = None
    booking_timestamp: str


class SettlementResponse(StrictBaseModel):
    trade_id: str
    settlement_status: str
    instruction_status: str
    ssi_id: str | None = None
    custodian: str
    depository: str
    fail_reason_code: str
    actual_settlement_date: str
    intended_settlement_date: str


class SSIResponse(StrictBaseModel):
    ssi_id: str
    counterparty_id: str
    market: str
    currency: str
    account_no: str
    bic: str
    custodian: str
    effective_from: str
    effective_to: str
    active_flag: bool


class CounterpartyResponse(StrictBaseModel):
    counterparty_id: str
    counterparty_name: str
    lei: str
    bic: str
    region: str
    default_market: str
    risk_rating: str
    active_flag: bool


class MarketCalendarResponse(StrictBaseModel):
    market: str
    calendar_date: str
    is_business_day: bool
    holiday_name: str | None = None


class SimilarHistoryResponse(StrictBaseModel):
    case_id: str
    exception_signature: str
    root_cause: str
    final_action: str
    human_override_flag: bool
    agent_confidence: float
    resolved_by: str
    resolution_time_hours: float
    outcome: str
    similarity_score: int = Field(default=0)
