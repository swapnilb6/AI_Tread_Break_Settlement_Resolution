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
│  │     └─ cases.py
│  │
│  ├─ ui/
│  │  ├─ __init__.py
│  │  └─ streamlit_app.py
│  │
│  ├─ schemas/
│  │  ├─ __init__.py
│  │  ├─ common.py
│  │  └─ case.py
│  │
│  ├─ db/
│  │  ├─ __init__.py
│  │  └─ session.py
│  │
│  ├─ rag/
│  │  ├─ __init__.py
│  │  ├─ chroma_client.py
│  │  ├─ ingest.py
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
│  └─ utils/
│     ├─ __init__.py
│     └─ logging.py
│
├─ storage/
│  └─ chroma/
│
├─ data/
│  └─ policies/
│
├─ requirements.txt
├─ Dockerfile
├─ docker-compose.yml
└─ .env.example
