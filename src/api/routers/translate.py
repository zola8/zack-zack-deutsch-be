import logging

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from api.dependencies import get_translator_service
from api.schemas.translation import TranslationRequest
from api.schemas.translation import TranslationResponse
from services.translator_service import TranslatorService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/translate", tags=["Translation"])


@router.post("/", response_model=TranslationResponse)
async def translate_text(
    request: TranslationRequest,
    translator: TranslatorService = Depends(get_translator_service)
):
    """
    Translate text between languages.
    """
    logger.debug("Received translation request: %s ", request.text[:100])

    if request.options:
        logger.debug("Received options: %s", request.options)
        # example: formality = request.options.get("formality", "default")

    try:
        result = await translator.translate(request)
        logger.debug("Translation completed successfully")
        return result
    except Exception as e:
        logger.error("Translation failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Translation service temporarily unavailable"
        )
