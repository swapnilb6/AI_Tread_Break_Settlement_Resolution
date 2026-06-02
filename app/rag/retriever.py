from app.rag.chroma_client import get_collection
from app.schemas.common import Citation
from app.schemas.case import RAGContext


def retrieve_policy_evidence(case_id: str, query: str, n_results: int = 5) -> RAGContext:
    collection = get_collection()

    results = collection.query(
        query_texts=[query],
        n_results=n_results,
    )

    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    ids = results.get("ids", [[]])[0]

    citations = []
    for chunk_id, metadata in zip(ids, metas):
        citations.append(
            Citation(
                doc_name=metadata.get("doc_name", "unknown"),
                section_heading=metadata.get("section_heading"),
                source_path=metadata.get("source_path"),
                chunk_id=chunk_id,
            )
        )

    return RAGContext(
        case_id=case_id,
        query=query,
        retrieved_chunks=docs,
        citations=citations,
        retrieval_confidence=0.60 if docs else 0.0,
        contradictions_found=False,
    )