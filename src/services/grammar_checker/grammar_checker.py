import logging

import httpx

from core.config import settings

logger = logging.getLogger(__name__)


class GrammarChecker:
    """Service for checking grammar by calling a persistent LanguageTool HTTP server."""

    def __init__(self, language: str = "de-DE"):
        self.language = language
        # Async client with connection pooling for performance
        self.client = httpx.AsyncClient(timeout=30.0)

    async def check(self, text: str, language: str | None = None) -> list[dict]:
        """
        Check the grammar of the provided text.
        """
        if not text or not text.strip():
            return []

        target_lang = language or self.language
        logger.info("Checking grammar for language: %s, length: %d", target_lang, len(text))

        payload = {
            "text": text,
            "language": target_lang
        }

        try:
            response = await self.client.post(url=settings.LANGUAGETOOL_API_URL, data=payload)
            response.raise_for_status()
            data = response.json()

            matches = data.get("matches", [])
            result = []

            for match in matches:
                replacements = [r.get("value") for r in match.get("replacements", [])]

                result.append({
                    "message": match.get("message", ""),
                    "replacements": replacements,
                    "offset": match.get("offset", 0),
                    "error_length": match.get("length", 0),
                    "context": {
                        "text": match.get("context", {}).get("text", ""),
                        "offset_in_context": match.get("context", {}).get("offset", 0)
                    },
                    "rule": {
                        "id": match.get("rule", {}).get("id", ""),
                        "category": match.get("rule", {}).get("category", {}).get("id", ""),
                        "issue_type": match.get("rule", {}).get("issueType", "")
                    },
                    "sentence": match.get("sentence", "")
                })

            return result

        except httpx.HTTPStatusError as e:
            logger.error("LanguageTool HTTP error: %s - %s", e.response.status_code, e.response.text)
            raise
        except httpx.RequestError as e:
            logger.error("LanguageTool connection error: %s", e)
            raise

    async def close(self) -> None:
        """Close the HTTP client to free up resources."""
        await self.client.aclose()
