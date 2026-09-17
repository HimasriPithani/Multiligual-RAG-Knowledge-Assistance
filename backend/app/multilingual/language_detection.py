"""
Detects the language of an incoming question — fully offline, free,
no external API call (uses the `langdetect` library).
"""

import logging

from langdetect import DetectorFactory, LangDetectException, detect

from app.config import settings

# Makes langdetect deterministic (it's probabilistic by default).
DetectorFactory.seed = 0

logger = logging.getLogger(__name__)


def detect_language(text: str) -> str:
    """
    Returns an ISO 639-1-ish language code (e.g. "en", "hi", "te").

    Falls back to "en" if detection fails (e.g. very short input) so the
    rest of the pipeline always has a usable language code to work with.
    """
    try:
        code = detect(text)
    except LangDetectException:
        logger.warning("Language detection failed for query, defaulting to English")
        return "en"

    return code


def language_display_name(code: str) -> str:
    return settings.supported_languages.get(code, code)
