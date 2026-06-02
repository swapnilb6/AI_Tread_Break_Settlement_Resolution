# app/tools/rag_tools.py
from __future__ import annotations

from typing import Any, Dict, List, Tuple

from app.rag.retriever import retrieve_policy_evidence as retrieve_policy_context
from app.schemas.agent_outputs import DataEvidenceRef, PolicyEvidence, ToolExecutionRecord


def _normalize_chunk(chunk: Any, idx: int) -> PolicyEvidence:
    """
    Accepts multiple possible shapes:
    - dict
    - Document-like object with .page_content and .metadata
    - custom retriever result with attributes
    """
    if isinstance(chunk, dict):
        metadata = chunk.get("metadata", {}) or {}
        excerpt = chunk.get("page_content") or chunk.get("content") or ""
        score = float(chunk.get("score", chunk.get("relevance_score", 0.0)))
    else:
        metadata = getattr(chunk, "metadata", {}) or {}
        excerpt = getattr(chunk, "page_content", None) or getattr(chunk, "content", "") or ""
        score = float(getattr(chunk, "score", getattr(chunk, "relevance_score", 0.0)) or 0.0)

    return PolicyEvidence(
        doc_name=str(metadata.get("doc_name", "unknown_doc")),
        doc_type=metadata.get("doc_type"),
        section_heading=metadata.get("section_heading"),
        exception_type=metadata.get("exception_type"),
        market=metadata.get("market"),
        version=metadata.get("version"),
        effective_date=metadata.get("effective_date"),
        source_path=metadata.get("source_path"),
        excerpt=excerpt[:1500],
        relevance_score=max(0.0, min(score, 1.0)),
        evidence_id=f"policy_{idx}",
    )


def retrieve_policy_evidence(
    query: str,
    exception_type: str,
    market: str | None,
    top_k: int = 5,
) -> Tuple[List[PolicyEvidence], ToolExecutionRecord]:
    try:
        from app.rag.retriever import retrieve_policy_evidence as retrieve_rag_context
        
        # Call the existing RAG retriever (doesn't require case_id at tools level)
        rag_context = retrieve_rag_context(
            case_id="temp",  # Temporary ID for tool-level call
            query=query,
            exception_type=exception_type,
            market=market,
            top_k=top_k,
        )

        # Convert RAGContext chunks and citations to PolicyEvidence objects
        normalized = []
        for idx, (chunk_text, citation) in enumerate(
            zip(rag_context.retrieved_chunks, rag_context.citations), start=1
        ):
            metadata = {
                "doc_name": citation.doc_name,
                "section_heading": citation.section_heading,
                "source_path": citation.source_path,
                "chunk_id": citation.chunk_id,
                "exception_type": exception_type,
                "market": market,
            }
            policy_ev = PolicyEvidence(
                doc_name=citation.doc_name,
                doc_type="policy_sop",
                section_heading=citation.section_heading,
                exception_type=exception_type,
                market=market,
                version=None,
                effective_date=None,
                source_path=citation.source_path,
                excerpt=chunk_text[:1500],
                relevance_score=rag_context.retrieval_confidence,
                evidence_id=citation.chunk_id or f"policy_{idx}",
            )
            normalized.append(policy_ev)

        return normalized, ToolExecutionRecord(
            tool_name="retrieve_policy_evidence",
            arguments={
                "query": query,
                "exception_type": exception_type,
                "market": market,
                "top_k": top_k,
            },
            status="SUCCESS",
            record_count=len(normalized),
            output_summary=f"{len(normalized)} policy chunk(s) retrieved",
        )
    except Exception as exc:
        return [], ToolExecutionRecord(
            tool_name="retrieve_policy_evidence",
            arguments={
                "query": query,
                "exception_type": exception_type,
                "market": market,
                "top_k": top_k,
            },
            status="ERROR",
            error_message=str(exc),
        )


def build_policy_evidence_refs(policy_chunks: List[PolicyEvidence]) -> List[DataEvidenceRef]:
    refs: List[DataEvidenceRef] = []
    for item in policy_chunks:
        refs.append(
            DataEvidenceRef(
                source_type="policy_chunk",
                source_id=item.evidence_id,
                description=f"{item.doc_name} / {item.section_heading or 'Unspecified section'}",
                fields_used=[
                    "doc_name",
                    "section_heading",
                    "excerpt",
                    "relevance_score",
                    "version",
                    "effective_date",
                ],
            )
        )
    return refs

