from __future__ import annotations

import argparse
from pathlib import Path

from app.rag.chroma_client import get_collection, reset_collection
from app.rag.chunker import chunk_document
from app.rag.document_loader import load_documents
from app.rag.embedder import OpenAIEmbedder
from app.rag.metadata_enricher import enrich_chunk_metadata


def build_index(policy_dir: str | Path, reset: bool = False) -> dict:
    if reset:
        reset_collection()

    collection = get_collection()
    embedder = OpenAIEmbedder()

    documents = load_documents(policy_dir)

    all_chunks = []
    for document in documents:
        all_chunks.extend(chunk_document(document))

    if not all_chunks:
        return {"documents": 0, "chunks": 0}

    texts = [chunk.text for chunk in all_chunks]
    embeddings = embedder.embed_texts(texts)

    collection.add(
        ids=[chunk.chunk_id for chunk in all_chunks],
        documents=texts,
        metadatas=[enrich_chunk_metadata(chunk) for chunk in all_chunks],
        embeddings=embeddings,
    )

    return {
        "documents": len(documents),
        "chunks": len(all_chunks),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Chroma policy knowledge base index")
    parser.add_argument("--policy-dir", default="data/policies", help="Directory containing policy documents")
    parser.add_argument("--reset", action="store_true", help="Reset collection before indexing")
    args = parser.parse_args()

    result = build_index(policy_dir=args.policy_dir, reset=args.reset)
    print("Chroma index build completed successfully")
    print(result)


if __name__ == "__main__":
    main()