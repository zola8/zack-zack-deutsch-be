import logging

import httpx
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from api.dependencies import get_grammar_checker
from api.schemas.grammar import GrammarCheckRequest
from api.schemas.grammar import GrammarCheckResponse
from services.grammar_checker_service import GrammarChecker

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/grammar", tags=["Grammar"])


@router.post("/check", response_model=GrammarCheckResponse)
async def check_grammar(
    request: GrammarCheckRequest,
    checker: GrammarChecker = Depends(get_grammar_checker),
):
    """
    Check the grammar of the provided text.
    """
    logger.info("Received grammar check request for %d chars", len(request.text))

    try:
        # Await the async HTTP call
        matches = await checker.check(request.text)

        logger.info("Grammar check completed: %d issues found", len(matches))

        return GrammarCheckResponse(
            text=request.text,
            language="de",
            matches=matches,
            match_count=len(matches),
            provider="languagetool",
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Grammar checking service is currently unavailable. Is the LanguageTool server running?"
        )
    except Exception as e:
        logger.error("Grammar check failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during grammar checking"
        )
