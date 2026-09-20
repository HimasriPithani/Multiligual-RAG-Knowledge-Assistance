"""
Central configuration for the whole backend.

Every value is read from environment variables.
The LLM runs locally through Ollama, so no cloud API key is required.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Local LLM - Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:3b-instruct"  # or qwen3:4b, but qwen2.5 is faster and cheaper

    # MongoDB
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "rag_assistant"

    # ChromaDB
    chroma_path: str = "./data/chroma"
    chroma_collection_name: str = "documents"

    # Embeddings
    embedding_model: str = (
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    # Chunking / retrieval
    chunk_size_words: int = 350
    chunk_overlap_words: int = 60
    top_k: int = 5
    similarity_threshold: float = 0.20

    # Uploads
    upload_dir: str = "./data/uploads"
    max_file_size_mb: int = 20

    # Supported languages
    supported_languages: dict = {
        "en": "English",
        "hi": "Hindi",
        "te": "Telugu",
        "mai": "Maithili",
    }


settings = Settings()