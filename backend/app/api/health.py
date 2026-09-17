from fastapi import APIRouter

from app.database import chroma, metadata
from app.models.schemas import HealthResponse
from app.rag.embeddings import get_embedding_model

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

    overall = "healthy" if (embedding_ok and vector_ok and metadata_ok) else "degraded"

    return HealthResponse(
        status=overall,
        embedding_model_loaded=embedding_ok,
        vector_db_connected=vector_ok,
        metadata_db_connected=metadata_ok,
    )
