from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.db.init_db import init_db
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
from app.db.session import SessionLocal


TABLE_LOAD_ORDER = [
    ("counterparties.csv", CounterpartyModel),
    ("ssi_master.csv", SSIMasterModel),
    ("market_calendar.csv", MarketCalendarModel),
    ("trades.csv", TradeModel),
    ("settlements.csv", SettlementModel),
    ("trade_exceptions.csv", TradeExceptionModel),
    ("ops_notes.csv", OpsNoteModel),
    ("resolution_history.csv", ResolutionHistoryModel),
]


def normalize_records(df: pd.DataFrame) -> list[dict]:
    records = df.where(pd.notnull(df), None).to_dict(orient="records")
    return records


def load_csv_to_table(db: Session, csv_path: Path, model_class: type) -> int:
    df = pd.read_csv(csv_path)
    records = normalize_records(df)

    db.execute(delete(model_class))
    if records:
        db.bulk_insert_mappings(model_class, records)

    return len(records)


def main() -> None:
    parser = argparse.ArgumentParser(description="Load synthetic CSV datasets into Postgres.")
    parser.add_argument("--data-dir", default="data/synthetic", help="Directory containing CSV files")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    init_db()

    with SessionLocal() as db:
        summary: dict[str, int] = {}

        for filename, model_class in TABLE_LOAD_ORDER:
            csv_path = data_dir / filename
            if not csv_path.exists():
                raise FileNotFoundError(f"Missing required file: {csv_path}")

            inserted = load_csv_to_table(db, csv_path, model_class)
            summary[filename] = inserted

        db.commit()

    print("Postgres load completed successfully")
    print(summary)


if __name__ == "__main__":
    main()