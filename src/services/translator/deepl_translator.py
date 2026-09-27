import logging

import deepl

from api.schemas.translation import TranslationRequest
from api.schemas.translation import TranslationResponse
from core.config import settings
from services.translator.base import BaseTranslator

logger = logging.getLogger(__name__)


class DeepLTranslator(BaseTranslator):
    """DeepL translation provider."""

    _client: deepl.DeepLClient | None = None

    @classmethod
    def _get_client(self) -> deepl.DeepLClient:
        """Get or create the DeepL client instance."""
        if self._client is None:
            logger.info("Initializing DeepL client")
            self._client = deepl.DeepLClient(settings.DEEPL_API_KEY)
        return self._client

    def get_provider_name(self) -> str:
        return "deepl"

    async def translate(self, request: TranslationRequest) -> TranslationResponse:
        logger.info("Translating with DeepL: %d chars", len(request.text))

        formality = request.options.get("formality") if request.options else None

        translate_kwargs = {
            "target_lang": request.target_lang,
            "source_lang": request.source_lang,
        }

        if formality:
            translate_kwargs["formality"] = formality

        try:
            client = self._get_client()
            result = client.translate_text(request.text, **translate_kwargs)
            logger.debug("DeepL translation successful")

            detected_source_language = getattr(result, "detected_source_lang", None)
            billed_characters = getattr(result, "billed_characters", None)

            return TranslationResponse(
                translated_text=result.text,
                source_lang=request.source_lang,
                target_lang=request.target_lang,
                char_count=len(request.text),
                provider=self.get_provider_name(),
                metadata={
                    "detected_source_language": detected_source_language,
                    "billed_characters": billed_characters,
                }
            )

        except deepl.DeepLException as e:
            logger.error("DeepL API error: %s", e, exc_info=True)
            raise
