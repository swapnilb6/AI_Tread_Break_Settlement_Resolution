from fastapi import APIRouter

from app.db.session import check_db_health
from app.rag.chroma_client import check_chroma_health

router = APIRouter()


@router.get("")
def health_check():
    return {
        "status": "ok",
        "postgres": "up" if check_db_health() else "down",
        "chroma": "up" if check_chroma_health() else "down",
    }