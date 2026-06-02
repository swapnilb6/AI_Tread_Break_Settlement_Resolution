from __future__ import annotations

import hashlib
from pathlib import Path

from app.schemas.rag import PolicyDocument


SUPPORTED_EXTENSIONS = {".md", ".txt"}


def _parse_front_matter(raw_text: str) -> tuple[dict, str]:
    """
    Very lightweight YAML-like front matter parser.
    Expected format:

    ---
    doc_name: failed settlement SOP
    doc_type: SOP
    market: ALL
    version: v1.0
    effective_date: 2026-01-01
    exception_type: FAILED_SETTLEMENT
    ---
    # Heading
    body...
    """
    if not raw_text.startswith("---"):
        return {}, raw_text

    lines = raw_text.splitlines()
    if len(lines) < 3:
        return {}, raw_text

    end_idx = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_idx = idx
            break

    if end_idx is None:
        return {}, raw_text

    metadata_lines = lines[1:end_idx]
    body = "\n".join(lines[end_idx + 1 :]).strip()

    metadata = {}
    for line in metadata_lines:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip()

    return metadata, body


def _build_doc_id(source_path: str) -> str:
    return hashlib.md5(source_path.encode("utf-8")).hexdigest()


def load_documents(data_dir: str | Path) -> list[PolicyDocument]:
    root = Path(data_dir)
    if not root.exists():
        raise FileNotFoundError(f"Policy directory not found: {root}")

    documents: list[PolicyDocument] = []

    for file_path in sorted(root.rglob("*")):
        if not file_path.is_file() or file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        raw_text = file_path.read_text(encoding="utf-8")
        front_matter, body = _parse_front_matter(raw_text)

        doc_name = front_matter.get("doc_name", file_path.stem.replace("_", " "))
        doc_type = front_matter.get("doc_type", "POLICY")

        documents.append(
            PolicyDocument(
                doc_id=_build_doc_id(str(file_path.resolve())),
                doc_name=doc_name,
                doc_type=doc_type,
                content=body,
                metadata=front_matter,
                source_path=str(file_path.as_posix()),
            )
        )

    return documents