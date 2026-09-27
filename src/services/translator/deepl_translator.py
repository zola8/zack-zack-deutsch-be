import logging

from api.schemas.translation import TranslationRequest
from api.schemas.translation import TranslationResponse
from services.translator.base import BaseTranslator

logger = logging.getLogger(__name__)


class DeepLTranslator(BaseTranslator):
    """DeepL translation provider."""

    def get_provider_name(self) -> str:
        return "deepl"

    async def translate(self, request: TranslationRequest) -> TranslationResponse:
        logger.info("Translating with DeepL: %d chars", len(request.text))

        formality = request.options.get("formality", "default") if request.options else "default"

        # TODO: Call DeepL API
        # For now, placeholder
        translated_text = f"[DeepL] {request.text} (formality: {formality})"

        return TranslationResponse(
            translated_text=translated_text,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
            char_count=len(request.text),
            provider=self.get_provider_name()
        )
