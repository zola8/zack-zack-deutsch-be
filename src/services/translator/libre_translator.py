import logging

from api.schemas.translation import TranslationRequest
from api.schemas.translation import TranslationResponse
from services.translator.base import BaseTranslator

logger = logging.getLogger(__name__)


class LibreTranslateTranslator(BaseTranslator):
    """LibreTranslate translation provider."""

    def get_provider_name(self) -> str:
        return "libre"

    async def translate(self, request: TranslationRequest) -> TranslationResponse:
        logger.info("Translating with LibreTranslate: %d chars", len(request.text))

        api_key = request.options.get("api_key") if request.options else None

        # TODO: Call LibreTranslate API
        # For now, placeholder
        translated_text = f"[LibreTranslate] {request.text}"

        return TranslationResponse(
            translated_text=translated_text,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
            char_count=len(request.text),
            provider=self.get_provider_name()
        )
