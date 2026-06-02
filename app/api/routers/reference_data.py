from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.reference_data_repo import ReferenceDataRepository
from app.schemas.reference_data import (
    CounterpartyResponse,
    MarketCalendarResponse,
    SettlementResponse,
    SimilarHistoryResponse,
    SSIResponse,
    TradeResponse,
)
from app.services.retrieval_service import RetrievalService

router = APIRouter()


def get_service(db: Session = Depends(get_db)) -> RetrievalService:
    repo = ReferenceDataRepository(db)
    return RetrievalService(repo)


@router.get("/trade/{trade_id}", response_model=TradeResponse)
def get_trade(trade_id: str, service: RetrievalService = Depends(get_service)):
    result = service.get_trade(trade_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Trade not found for trade_id={trade_id}")
    return result


@router.get("/settlement/{trade_id}", response_model=SettlementResponse)
def get_settlement(trade_id: str, service: RetrievalService = Depends(get_service)):
    result = service.get_settlement(trade_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Settlement not found for trade_id={trade_id}")
    return result


@router.get("/ssi/{counterparty_id}", response_model=list[SSIResponse])
def get_ssi(counterparty_id: str, service: RetrievalService = Depends(get_service)):
    return service.get_ssi(counterparty_id)


@router.get("/counterparty/{counterparty_id}", response_model=CounterpartyResponse)
def get_counterparty(counterparty_id: str, service: RetrievalService = Depends(get_service)):
    result = service.get_counterparty(counterparty_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Counterparty not found for counterparty_id={counterparty_id}")
    return result


@router.get("/calendar/{market}/{calendar_date}", response_model=MarketCalendarResponse)
def get_calendar_day(market: str, calendar_date: str, service: RetrievalService = Depends(get_service)):
    result = service.get_calendar_day(market=market, calendar_date=calendar_date)
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Calendar day not found for market={market}, date={calendar_date}",
        )
    return result


@router.get("/history/similar", response_model=list[SimilarHistoryResponse])
def get_similar_history(
    signature: str = Query(..., description="Format: EXCEPTION_TYPE|MARKET|CURRENCY|COUNTERPARTY_ID"),
    limit: int = Query(default=5, ge=1, le=20),
    service: RetrievalService = Depends(get_service),
):
    return service.get_similar_history(signature=signature, limit=limit)
