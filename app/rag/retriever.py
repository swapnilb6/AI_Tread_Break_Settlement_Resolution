from __future__ import annotations

from app.config import get_settings
from app.rag.chroma_client import get_collection
from app.rag.embedder import OpenAIEmbedder
from app.schemas.case import RAGContext
from app.schemas.common import Citation
from app.schemas.rag import RetrievalHit

settings = get_settings()


def _distance_to_score(distance: float | None) -> float:
    if distance is None:
        return 0.0
    return round(1.0 / (1.0 + max(distance, 0.0)), 4)


def retrieve_policy_evidence(
    case_id: str,
    query: str,
    exception_type: str | None = None,
    market: str | None = None,
    top_k: int | None = None,
) -> RAGContext:
    collection = get_collection()
    embedder = OpenAIEmbedder()
    query_embedding = embedder.embed_query(query)

    where = {}
    if exception_type and exception_type != "UNKNOWN":
        where["exception_type"] = {"$in": [exception_type, "ALL"]}
    if market and market != "UNKNOWN":
        where["market"] = {"$in": [market, "ALL"]}

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k or settings.rag_top_k,
        where=where or None,
    )

    ids = results.get("ids", [[]])[0]
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    hits: list[RetrievalHit] = []

    for chunk_id, text, metadata, distance in zip(ids, docs, metas, distances):
        score = _distance_to_score(distance)
        citation = Citation(
            doc_name=metadata.get("doc_name", "unknown"),
            section_heading=metadata.get("section_heading"),
            source_path=metadata.get("source_path"),
            chunk_id=chunk_id,
        )
        hits.append(
            RetrievalHit(
                chunk_id=chunk_id,
                text=text,
                score=score,
                citation=citation,
                metadata=metadata,
            )
        )

    avg_score = round(sum(hit.score for hit in hits) / len(hits), 4) if hits else 0.0

    return RAGContext(
        case_id=case_id,
        query=query,
        retrieved_chunks=[hit.text for hit in hits],
        citations=[hit.citation for hit in hits],
        retrieval_confidence=avg_score,
        contradictions_found=False,
    )