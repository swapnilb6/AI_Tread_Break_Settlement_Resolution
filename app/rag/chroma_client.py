import chromadb

from app.config import get_settings

settings = get_settings()


def get_chroma_client() -> chromadb.PersistentClient:
    return chromadb.PersistentClient(path=settings.chroma_path)


def get_collection():
    client = get_chroma_client()
    return client.get_or_create_collection(name=settings.chroma_collection)


def check_chroma_health() -> bool:
    try:
        client = get_chroma_client()
        client.heartbeat()
        return True
    except Exception:
        return False