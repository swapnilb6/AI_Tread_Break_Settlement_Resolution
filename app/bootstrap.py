from __future__ import annotations

import argparse
import sys
from pathlib import Path


def run_db_init() -> None:
    from app.db.init_db import init_db

    print("[bootstrap] Initializing database schema...")
    init_db()
    print("[bootstrap] Database schema initialization completed.")


def run_postgres_seed(data_dir: str) -> None:
    """
    Reuse the existing CLI-style loader by temporarily setting sys.argv.
    Your current loader already supports:
      python -m app.synthetic_data.load_to_postgres --data-dir <path>
    """
    from app.synthetic_data.load_to_postgres import main as load_main

    print(f"[bootstrap] Loading synthetic/reference CSV data from: {data_dir}")
    original_argv = sys.argv[:]
    try:
        sys.argv = [
            "load_to_postgres",
            "--data-dir",
            data_dir,
        ]
        load_main()
    finally:
        sys.argv = original_argv

    print("[bootstrap] Postgres seed load completed.")



def run_rag_ingest(policy_dir: str) -> None:
    from pathlib import Path

    from app.rag.document_loader import load_documents
    from app.rag.chunker import chunk_document
    from app.rag.metadata_enricher import enrich_chunk_metadata
    from app.rag.ingest import ingest_documents

    base_path = Path(policy_dir)
    if not base_path.exists():
        raise FileNotFoundError(f"Policy directory not found: {base_path}")

    print(f"[bootstrap] Loading policy documents from: {base_path}")
    raw_documents = load_documents(base_path)
    print(f"[bootstrap] Loaded {len(raw_documents)} raw policy document(s).")

    if not raw_documents:
        print("[bootstrap] No policy documents found. Skipping RAG ingest.")
        return

    ingest_payload = []

    for document in raw_documents:
        chunks = chunk_document(document)
        for chunk in chunks:
            enriched_metadata = enrich_chunk_metadata(chunk)
            ingest_payload.append(
                {
                    "text": chunk.text,
                    "metadata": enriched_metadata,
                }
            )

    inserted_count = ingest_documents(ingest_payload)
    print(f"[bootstrap] Chroma ingest completed. Inserted {inserted_count} chunk(s).")


def main() -> None:
    parser = argparse.ArgumentParser(description="Bootstrap DB + synthetic data + RAG knowledge base.")
    parser.add_argument(
        "--data-dir",
        default="/app/data/synthetic",
        help="Directory containing synthetic CSV files.",
    )
    parser.add_argument(
        "--policy-dir",
        default="/app/data/policies",
        help="Directory containing policy/SOP markdown/text documents.",
    )
    parser.add_argument(
        "--skip-db-init",
        action="store_true",
        help="Skip DB schema initialization.",
    )
    parser.add_argument(
        "--skip-db-seed",
        action="store_true",
        help="Skip Postgres CSV data load.",
    )
    parser.add_argument(
        "--skip-rag",
        action="store_true",
        help="Skip RAG knowledge base ingestion.",
    )

    args = parser.parse_args()

    print("[bootstrap] Starting environment bootstrap...")

    if not args.skip_db_init:
        run_db_init()

    if not args.skip_db_seed:
        run_postgres_seed(args.data_dir)

    if not args.skip_rag:
        run_rag_ingest(args.policy_dir)

    print("[bootstrap] Bootstrap completed successfully.")


if __name__ == "__main__":
    main()
