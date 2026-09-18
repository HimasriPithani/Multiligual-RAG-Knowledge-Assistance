from fastapi import APIRouter

from app.database import chroma, metadata
from app.models.schemas import HealthResponse
from app.rag.embeddings import get_embedding_model
from app.rag.generator import check_ollama

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    embedding_ok = True
    try:
        get_embedding_model()
    except Exception:
        embedding_ok = False

    vector_ok = chroma.health_check()
    metadata_ok = await metadata.health_check()
    ollama_ok, ollama_model_ok = check_ollama()

    overall = (
        "healthy"
        if (embedding_ok and vector_ok and metadata_ok and ollama_ok and ollama_model_ok)
        else "degraded"
    )

    return HealthResponse(
        status=overall,
        embedding_model_loaded=embedding_ok,
        vector_db_connected=vector_ok,
        metadata_db_connected=metadata_ok,
        ollama_connected=ollama_ok,
        ollama_model_available=ollama_model_ok,
    )
