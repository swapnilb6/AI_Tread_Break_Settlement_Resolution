from sqlalchemy import Boolean, Date, DateTime, Float, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TradeExceptionModel(Base):
    __tablename__ = "trade_exceptions"

    exception_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    trade_id: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    exception_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    detected_timestamp: Mapped[str] = mapped_column(String(64), nullable=False)
    source_channel: Mapped[str] = mapped_column(String(64), nullable=False)
    priority: Mapped[str] = mapped_column(String(16), nullable=False)
    severity: Mapped[str] = mapped_column(String(16), nullable=False)
    free_text_summary: Mapped[str] = mapped_column(Text, nullable=False)
    counterparty_id: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    market: Mapped[str] = mapped_column(String(16), index=True, nullable=False)
    asset_class: Mapped[str] = mapped_column(String(64), nullable=False)
    settlement_date: Mapped[str] = mapped_column(String(32), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(16), nullable=False)
    current_status: Mapped[str] = mapped_column(String(32), nullable=False)
    ground_truth_root_cause: Mapped[str] = mapped_column(String(128), nullable=False)
    ground_truth_action: Mapped[str] = mapped_column(Text, nullable=False)
    resolution_sla_hours: Mapped[int] = mapped_column(Integer, nullable=False)


class TradeModel(Base):
    __tablename__ = "trades"

    trade_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    trade_date: Mapped[str] = mapped_column(String(32), nullable=False)
    book: Mapped[str] = mapped_column(String(64), nullable=False)
    trader: Mapped[str] = mapped_column(String(64), nullable=False)
    instrument: Mapped[str] = mapped_column(String(64), nullable=False)
    side: Mapped[str] = mapped_column(String(16), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    counterparty_id: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    account: Mapped[str] = mapped_column(String(64), nullable=True)
    market: Mapped[str] = mapped_column(String(16), index=True, nullable=False)
    currency: Mapped[str] = mapped_column(String(16), nullable=False)
    settlement_date: Mapped[str] = mapped_column(String(32), nullable=False)
    isin: Mapped[str] = mapped_column(String(32), nullable=True)
    booking_timestamp: Mapped[str] = mapped_column(String(64), nullable=False)


class SettlementModel(Base):
    __tablename__ = "settlements"

    trade_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    settlement_status: Mapped[str] = mapped_column(String(32), nullable=False)
    instruction_status: Mapped[str] = mapped_column(String(32), nullable=False)
    ssi_id: Mapped[str] = mapped_column(String(64), nullable=True)
    custodian: Mapped[str] = mapped_column(String(128), nullable=False)
    depository: Mapped[str] = mapped_column(String(128), nullable=False)
    fail_reason_code: Mapped[str] = mapped_column(String(64), nullable=False)
    actual_settlement_date: Mapped[str] = mapped_column(String(32), nullable=False)
    intended_settlement_date: Mapped[str] = mapped_column(String(32), nullable=False)


class SSIMasterModel(Base):
    __tablename__ = "ssi_master"

    ssi_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    counterparty_id: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    market: Mapped[str] = mapped_column(String(16), index=True, nullable=False)
    currency: Mapped[str] = mapped_column(String(16), nullable=False)
    account_no: Mapped[str] = mapped_column(String(64), nullable=False)
    bic: Mapped[str] = mapped_column(String(64), nullable=False)
    custodian: Mapped[str] = mapped_column(String(128), nullable=False)
    effective_from: Mapped[str] = mapped_column(String(32), nullable=False)
    effective_to: Mapped[str] = mapped_column(String(32), nullable=False)
    active_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class CounterpartyModel(Base):
    __tablename__ = "counterparties"

    counterparty_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    counterparty_name: Mapped[str] = mapped_column(String(128), nullable=False)
    lei: Mapped[str] = mapped_column(String(64), nullable=False)
    bic: Mapped[str] = mapped_column(String(64), nullable=False)
    region: Mapped[str] = mapped_column(String(32), nullable=False)
    default_market: Mapped[str] = mapped_column(String(16), nullable=False)
    risk_rating: Mapped[str] = mapped_column(String(16), nullable=False)
    active_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class MarketCalendarModel(Base):
    __tablename__ = "market_calendar"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    market: Mapped[str] = mapped_column(String(16), index=True, nullable=False)
    calendar_date: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    is_business_day: Mapped[bool] = mapped_column(Boolean, nullable=False)
    holiday_name: Mapped[str] = mapped_column(String(128), nullable=True)


class OpsNoteModel(Base):
    __tablename__ = "ops_notes"

    note_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    exception_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    note_timestamp: Mapped[str] = mapped_column(String(64), nullable=False)
    note_type: Mapped[str] = mapped_column(String(32), nullable=False)
    author: Mapped[str] = mapped_column(String(64), nullable=False)
    note_text: Mapped[str] = mapped_column(Text, nullable=False)
    attachment_text: Mapped[str] = mapped_column(Text, nullable=True)
    contains_adversarial_text: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class ResolutionHistoryModel(Base):
    __tablename__ = "resolution_history"

    case_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    exception_signature: Mapped[str] = mapped_column(String(256), index=True, nullable=False)
    root_cause: Mapped[str] = mapped_column(String(128), nullable=False)
    final_action: Mapped[str] = mapped_column(Text, nullable=False)
    human_override_flag: Mapped[bool] = mapped_column(Boolean, nullable=False)
    agent_confidence: Mapped[float] = mapped_column(Float, nullable=False)
    resolved_by: Mapped[str] = mapped_column(String(64), nullable=False)
    resolution_time_hours: Mapped[float] = mapped_column(Float, nullable=False)
    outcome: Mapped[str] = mapped_column(String(64), nullable=False)
