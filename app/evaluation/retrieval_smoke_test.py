from __future__ import annotations

import argparse

import httpx
import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(description="Smoke test retrieval endpoints.")
    parser.add_argument("--base-url", default="http://localhost:8000", help="FastAPI base URL")
    parser.add_argument("--data-dir", default="data/synthetic", help="Directory containing generated CSVs")
    args = parser.parse_args()

    data_dir = args.data_dir
    base_url = args.base_url.rstrip("/")

    trades = pd.read_csv(f"{data_dir}/trades.csv")
    counterparties = pd.read_csv(f"{data_dir}/counterparties.csv")
    calendar = pd.read_csv(f"{data_dir}/market_calendar.csv")
    history = pd.read_csv(f"{data_dir}/resolution_history.csv")

    sample_trade_id = trades.iloc[0]["trade_id"]
    sample_counterparty_id = counterparties.iloc[0]["counterparty_id"]
    sample_market = calendar.iloc[0]["market"]
    sample_date = calendar.iloc[0]["calendar_date"]
    sample_signature = history.iloc[0]["exception_signature"]

    endpoints = [
        f"{base_url}/trade/{sample_trade_id}",
        f"{base_url}/settlement/{sample_trade_id}",
        f"{base_url}/ssi/{sample_counterparty_id}",
        f"{base_url}/counterparty/{sample_counterparty_id}",
        f"{base_url}/calendar/{sample_market}/{sample_date}",
        f"{base_url}/history/similar?signature={sample_signature}",
    ]

    with httpx.Client(timeout=20.0) as client:
        for endpoint in endpoints:
            response = client.get(endpoint)
            print(endpoint, "->", response.status_code)
            response.raise_for_status()

    print("Retrieval smoke test passed successfully")


if __name__ == "__main__":
    main()