import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class LLMServiceError(Exception):
    pass


def check_ollama() -> bool:
    """Check whether Ollama is running and the configured model is available."""
    try:
        url = f"{settings.ollama_base_url.rstrip('/')}/api/tags"

        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()

        data = response.json()
        models = data.get("models", [])

        return any(
            model.get("name") == settings.ollama_model
            for model in models
        )

    except Exception as exc:
        logger.warning("Ollama health check failed: %s", exc)
        return False


def generate_answer(prompt: str) -> str:
    """Generate an answer using the local Ollama model."""

    url = f"{settings.ollama_base_url.rstrip('/')}/api/chat"

    payload = {
        "model": settings.ollama_model,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 256,
        },
        "keep_alive": "10m",
    }

    try:
        response = httpx.post(
            url,
            json=payload,
            timeout=300.0,
        )

        response.raise_for_status()

        data = response.json()

        message = data.get("message", {})
        answer = message.get("content", "").strip()

        if not answer:
            raise LLMServiceError(
                "The local AI model returned an empty response."
            )

        return answer

    except httpx.TimeoutException as exc:
        logger.exception("Ollama request timed out")
        raise LLMServiceError(
            "The local AI model took too long to respond."
        ) from exc

    except httpx.HTTPStatusError as exc:
        logger.exception("Ollama returned an HTTP error")
        raise LLMServiceError(
            "Ollama returned an error. Please check that the model "
            "is installed and Ollama is running."
        ) from exc

    except LLMServiceError:
        raise

    except Exception as exc:
        logger.exception("Ollama generation failed")
        raise LLMServiceError(
            "The local AI service is temporarily unavailable."
        ) from exc