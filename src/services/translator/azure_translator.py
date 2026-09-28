import logging
import uuid

import httpx

from api.schemas.translation import TranslationRequest
from api.schemas.translation import TranslationResponse
from core.config import settings
from services.translator.base import BaseTranslator

logger = logging.getLogger(__name__)


class AzureTranslator(BaseTranslator):
    """Azure Cognitive Services Translator provider."""

    def get_provider_name(self) -> str:
        return "azure"

    async def translate(self, request: TranslationRequest) -> TranslationResponse:
        logger.info("Translating with Azure Translator: %d chars", len(request.text))

        url = f"{settings.AZURE_TRANSLATOR_ENDPOINT}/translate"

        params = {
            'api-version': '3.0',
            'from': request.source_lang,
            'to': [request.target_lang],
        }

        headers = {
            "Ocp-Apim-Subscription-Key": settings.AZURE_TRANSLATOR_KEY,
            "Ocp-Apim-Subscription-Region": settings.AZURE_TRANSLATOR_REGION,
            "Content-type": "application/json",
            "X-ClientTraceId": str(uuid.uuid4()),
        }

        body = [{"text": request.text}]

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, params=params, headers=headers, json=body)
                response.raise_for_status()
                data = response.json()

                first_result = data[0]
                translations = first_result.get("translations", [])

                if not translations:
                    raise ValueError("No translations returned from Azure API")

                translated_text = translations[0].get("text", "")

                return TranslationResponse(
                    translated_text=translated_text,
                    source_lang=request.source_lang,
                    target_lang=request.target_lang,
                    char_count=len(request.text),
                    provider=self.get_provider_name(),
                    metadata=None
                )

        except httpx.HTTPStatusError as e:
            logger.error("Azure Translator HTTP error: %s - %s", e.response.status_code, e.response.text)
            raise
        except Exception as e:
            logger.error("Azure Translator error: %s", e, exc_info=True)
            raise
