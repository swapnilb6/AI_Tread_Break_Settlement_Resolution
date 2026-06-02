
[Streamlit UI]
      |
      v
[CrewAI Flow Orchestrator]
      |
      +--> Intake Agent
      +--> Retrieval Agent
      +--> Policy / RAG Agent
      +--> Root Cause Agent
      +--> Recommendation Agent
      +--> HITL Agent
      +--> Audit Agent
      |
      +--> FastAPI Dummy APIs
      +--> Postgres (case history, approvals, audit)
      +--> Chroma (document embeddings + retrieval)
      +--> Local synthetic CSV / docs / PDFs
