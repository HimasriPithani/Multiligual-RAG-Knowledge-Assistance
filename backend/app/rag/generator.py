import json
import logging
from typing import AsyncGenerator

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


async def generate_answer_stream(
    prompt: str,
) -> AsyncGenerator[str, None]:
    """
    Generate an answer from Ollama and stream the response
    token-by-token to the caller.
    """

    url = f"{settings.ollama_base_url.rstrip('/')}/api/chat"

    payload = {
        "model": settings.ollama_model,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "stream": True,
        "options": {
            "temperature": 0.1,
            "num_predict": 180,
        },
        "keep_alive": "30m",
    }

    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(
                connect=10.0,
                read=300.0,
                write=30.0,
                pool=30.0,
            )
        ) as client:

            async with client.stream(
                "POST",
                url,
                json=payload,
            ) as response:

                response.raise_for_status()

                async for line in response.aiter_lines():

                    if not line:
                        continue

                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError:
                        logger.warning(
                            "Could not decode Ollama stream line: %s",
                            line,
                        )
                        continue

                    message = data.get("message", {})
                    content = message.get("content", "")

                    if content:
                        yield content

                    if data.get("done") is True:
                        break

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
        logger.exception("Ollama streaming failed")

        raise LLMServiceError(
            "The local AI service is temporarily unavailable."
        ) from exc