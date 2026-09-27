import logging

from api.schemas.translation import TranslationRequest
from api.schemas.translation import TranslationResponse
from services.translator.factory import TranslatorFactory

logger = logging.getLogger(__name__)


class TranslatorService:
    """Service for handling text translation operations."""

    async def translate(self, request: TranslationRequest) -> TranslationResponse:
        logger.info(
            "Translating %d chars from %s to %s using %s",
            len(request.text),
            request.source_lang,
            request.target_lang,
            request.provider
        )

        # Get the appropriate translator
        translator = TranslatorFactory.get_translator(request.provider)

        # Delegate to the translator
        return await translator.translate(request)
