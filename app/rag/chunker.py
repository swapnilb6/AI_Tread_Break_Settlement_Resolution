from __future__ import annotations

import re
import uuid

from app.config import get_settings
from app.schemas.rag import DocumentChunk, PolicyDocument

settings = get_settings()

HEADING_PATTERN = re.compile(
    r"(?m)^(#{1,6}\s+.+|[A-Z][A-Z0-9 /&()_-]{3,}|(?:\d+\.)+\s+.+)$"
)


def split_by_heading(content: str) -> list[tuple[str, str]]:
    """
    Returns [(section_heading, section_text), ...]
    Supports markdown headings and simple uppercase/numbered headings.
    """
    matches = list(HEADING_PATTERN.finditer(content))

    if not matches:
        return [("GENERAL", content.strip())]

    sections: list[tuple[str, str]] = []

    for idx, match in enumerate(matches):
        heading = match.group(0).strip().lstrip("#").strip()
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(content)
        section_text = content[start:end].strip()
        if section_text:
            sections.append((heading, section_text))

    if not sections:
        return [("GENERAL", content.strip())]

    return sections


def bounded_chunks(text: str, chunk_size: int, overlap: int) -> list[str]:
    if len(text) <= chunk_size:
        return [text.strip()]

    chunks: list[str] = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        if end < len(text):
            last_break = max(
                chunk.rfind("\n\n"),
                chunk.rfind(". "),
                chunk.rfind("; "),
                chunk.rfind(" "),
            )
            if last_break > int(chunk_size * 0.6):
                chunk = chunk[:last_break].strip()

        if chunk.strip():
            chunks.append(chunk.strip())

        if end >= len(text):
            break

        start += max(len(chunk) - overlap, 1)

    return chunks


def chunk_document(document: PolicyDocument) -> list[DocumentChunk]:
    sections = split_by_heading(document.content)
    chunks: list[DocumentChunk] = []

    chunk_size = settings.rag_chunk_size
    overlap = settings.rag_chunk_overlap

    for section_heading, section_text in sections:
        for piece in bounded_chunks(section_text, chunk_size=chunk_size, overlap=overlap):
            chunks.append(
                DocumentChunk(
                    chunk_id=str(uuid.uuid4()),
                    doc_id=document.doc_id,
                    doc_name=document.doc_name,
                    doc_type=document.doc_type,
                    section_heading=section_heading,
                    text=piece,
                    metadata=dict(document.metadata),
                    source_path=document.source_path,
                )
            )

    return chunks