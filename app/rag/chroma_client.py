from __future__ import annotations

import chromadb

from app.config import get_settings

settings = get_settings()


def get_chroma_client() -> chromadb.PersistentClient:
    return chromadb.PersistentClient(path=settings.chroma_path)


def get_collection():
    client = get_chroma_client()
    return client.get_or_create_collection(name=settings.chroma_collection)


def reset_collection() -> None:
    client = get_chroma_client()
    try:
        client.delete_collection(name=settings.chroma_collection)
    except Exception:
        pass
    client.get_or_create_collection(name=settings.chroma_collection)


def check_chroma_health() -> bool:
    try:
        client = get_chroma_client()
        client.heartbeat()
        return True
    except Exception:
        return False