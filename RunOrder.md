Run order
1. Generate synthetic CSVs
Shellpython -m app.synthetic_data.generate_datasets --output-dir data/synthetic --num-cases 500 --seed 42
2. Start services
Shelldocker compose up --build
3. Load CSVs into Postgres
Shellpython -m app.synthetic_data.load_to_postgres --data-dir data/syntheticShow more lines
4. Smoke test retrieval APIs
Shellpython -m app.evaluation.retrieval_smoke_test --base-url http://localhost:8000 --data-dir data/synthetic