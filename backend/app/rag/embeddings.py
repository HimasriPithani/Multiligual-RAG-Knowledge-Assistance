"""
Wraps a free, locally-run multilingual Sentence Transformer model.

The model is downloaded once from Hugging Face (no API key, no cost)
and cached on disk. It's loaded as a singleton so every request reuses
the same in-memory model instead of reloading it.

Default model: paraphrase-multilingual-MiniLM-L12-v2
  - Supports 50+ languages including English, Hindi, and Telugu.
  - Small (~470MB) and fast enough to run on CPU, which matters since
    students usually don't have a paid GPU instance.
  - Maithili isn't explicitly in its training languages, but because the
    model shares subword vocabulary with Hindi (same Devanagari script
    and closely related grammar), retrieval quality is usually still
    reasonable. If you need stronger Maithili support later, swap
    EMBEDDING_MODEL to "intfloat/multilingual-e5-large" (larger, slower).
"""

from functools import lru_cache
from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer

from app.config import settings


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """Loads (or returns the cached) embedding model. Runs once per process."""
    return SentenceTransformer(settings.embedding_model)


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Embeds a batch of texts (document chunks) into vectors."""
    model = get_embedding_model()
    vectors: np.ndarray = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=False,
        normalize_embeddings=True,  # so cosine similarity == dot product
    )
    return vectors.tolist()


def embed_query(text: str) -> List[float]:
    """Embeds a single query string into a vector."""
    return embed_texts([text])[0]
