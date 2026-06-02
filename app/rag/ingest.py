import uuid
from typing import Iterable

from app.rag.chroma_client import get_collection


def ingest_documents(documents: Iterable[dict]) -> int:
    """
    Expected document shape:
    {
        "text": "...chunk text...",
        "metadata": {
            "doc_name": "...",
            "doc_type": "...",
            "section_heading": "...",
            "exception_type": "...",
            "market": "...",
            "version": "...",
            "effective_date": "...",
            "source_path": "..."
        }
    }
    """
    collection = get_collection()

    ids = []
    texts = []
    metadatas = []

    for doc in documents:
        ids.append(str(uuid.uuid4()))
        texts.append(doc["text"])
        metadatas.append(doc.get("metadata", {}))

    if not texts:
        return 0

    collection.add(
        ids=ids,
        documents=texts,
        metadatas=metadatas,
    )
    return len(texts)