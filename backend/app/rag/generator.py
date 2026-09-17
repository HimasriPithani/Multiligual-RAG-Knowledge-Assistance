"""
Generates the final answer using a local Ollama LLM.

The RAG pipeline passes a grounded prompt containing the retrieved
document chunks. Ollama runs locally on the user's machine, so no
external LLM API key is required.
"""

import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class LLMServiceError(Exception):
    """Raised when the local LLM cannot generate an answer."""

    pass


def generate_answer(prompt: str) -> str:
    """Generate an answer using the configured Ollama model."""

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
        "think": False,
        "keep_alive": "10m",
        "options": {
            "temperature": 0.2,
            "num_predict": 512,
        },
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
            "The local AI model took too long to respond. Please try again."
        ) from exc

    except httpx.HTTPStatusError as exc:
        logger.exception("Ollama returned an HTTP error")
        raise LLMServiceError(
            "The local AI service returned an error. "
            "Make sure Ollama is running and the model is available."
        ) from exc

    except LLMServiceError:
        raise

    except Exception as exc:
        logger.exception("Ollama generation failed")
        raise LLMServiceError(
            "The local AI service is temporarily unavailable. "
            "Please make sure Ollama is running."
        ) from exc