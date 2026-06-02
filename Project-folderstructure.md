# Project Folder Structure

```
project-root/
├─ app/
│  ├─ __init__.py
│  ├─ config.py
│  │
│  ├─ api/
│  │  ├─ __init__.py
│  │  ├─ main.py
│  │  └─ routers/
│  │     ├─ __init__.py
│  │     ├─ health.py
│  │     ├─ cases.py
│  │     └─ reference_data.py
│  │
│  ├─ ui/
│  │  ├─ __init__.py
│  │  └─ streamlit_app.py
│  │
│  ├─ schemas/
│  │  ├─ __init__.py
│  │  ├─ common.py
│  │  ├─ case.py
│  │  ├─ reference_data.py
│  │  └─ rag.py
│  │
│  ├─ db/
│  │  ├─ __init__.py
│  │  ├─ session.py
│  │  ├─ base.py
│  │  ├─ init_db.py
│  │  └─ models.py
│  │
│  ├─ repositories/
│  │  ├─ __init__.py
│  │  └─ reference_data_repo.py
│  │
│  ├─ services/
│  │  ├─ __init__.py
│  │  └─ retrieval_service.py
│  │
│  ├─ rag/
│  │  ├─ __init__.py
│  │  ├─ chroma_client.py
│  │  ├─ document_loader.py
│  │  ├─ chunker.py
│  │  ├─ metadata_enricher.py
│  │  ├─ embedder.py
│  │  ├─ index_builder.py
│  │  └─ retriever.py
│  │
│  ├─ agents/
│  │  ├─ __init__.py
│  │  └─ intake_agent.py
│  │
│  ├─ orchestration/
│  │  ├─ __init__.py
│  │  └─ flow.py
│  │
│  ├─ utils/
│  │  ├─ __init__.py
│  │  └─ logging.py
│  │
│  ├─ synthetic_data/
│  │  ├─ __init__.py
│  │  ├─ generate_datasets.py
│  │  └─ load_to_postgres.py
│  │
│  └─ evaluation/
│     ├─ __init__.py
│     └─ retrieval_smoke_test.py
│
├─ storage/
│  └─ chroma/
│
├─ data/
│  └─ policies/
│     ├─ failed_settlement_sop.md
│     ├─ ssi_validation_playbook.md
│     ├─ escalation_matrix.md
│     ├─ holiday_guidance.md
│     ├─ settlement_instruction_policy.md
│     ├─ audit_policy.md
│     └─ manual_override_guidelines.md
│
├─ requirements.txt
├─ Dockerfile
├─ docker-compose.yml
└─ .env.example
```

## Folder Structure Breakdown

### app/
Core application directory containing all business logic.

### app/api/
FastAPI routers and main application entry point.
- **routers/**: API route handlers
  - `reference_data.py`: Reference data endpoints

### app/schemas/
Pydantic models for request/response validation.
- `reference_data.py`: Reference data schemas
- `rag.py`: RAG-related schemas for documents and queries

### app/db/
Database configuration and models.
- `base.py`: SQLAlchemy base configuration
- `init_db.py`: Database initialization script
- `models.py`: Database models/ORM definitions
- `session.py`: Database session management

### app/repositories/
Data access layer (DAL) for database operations.
- `reference_data_repo.py`: Reference data repository

### app/services/
Business logic and service layer.
- `retrieval_service.py`: Data retrieval service

### app/synthetic_data/
Synthetic data generation and loading utilities.
- `load_to_postgres.py`: Script to load data into PostgreSQL

### app/evaluation/
Testing and quality assurance modules.
- `retrieval_smoke_test.py`: Smoke tests for retrieval functionality

### app/rag/
Retrieval-Augmented Generation (RAG) implementation.
- `chroma_client.py`: Chroma vector database client
- `document_loader.py`: Load and parse documents
- `chunker.py`: Split documents into chunks for embedding
- `metadata_enricher.py`: Enrich chunks with metadata
- `embedder.py`: Generate embeddings for documents
- `index_builder.py`: Build and manage vector indices
- `retriever.py`: Retrieve relevant documents for queries

### app/agents/
AI agents and orchestration.

### app/orchestration/
Workflow and process orchestration.

### app/ui/
User interface (Streamlit).

### storage/
External storage for vector databases and other data.

### data/
Static and reference data files.

### data/policies/
Policy documents and operational guidelines.
- `failed_settlement_sop.md`: Standard operating procedure for failed settlements
- `ssi_validation_playbook.md`: SSI validation guidelines
- `escalation_matrix.md`: Escalation procedures and matrix
- `holiday_guidance.md`: Holiday-specific guidance
- `settlement_instruction_policy.md`: Settlement instruction policies
- `audit_policy.md`: Audit and compliance policies
- `manual_override_guidelines.md`: Guidelines for manual overrides
