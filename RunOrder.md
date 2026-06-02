Run order
1. Generate synthetic CSVs
python -m app.synthetic_data.generate_datasets --output-dir data/synthetic --num-cases 500 --seed 42
2. Start services
docker compose up --build
3. Load CSVs into Postgres
python -m app.synthetic_data.load_to_postgres --data-dir data/synthetic
4. Smoke test retrieval APIs
python -m app.evaluation.retrieval_smoke_test --base-url http://localhost:8000 --data-dir data/synthetic
---------
2) Build index
python -m app.rag.index_builder --policy-dir data/policies --reset
3) Smoke test retrieval
python -m app.evaluation.rag_smoke_test