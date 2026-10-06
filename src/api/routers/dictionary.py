import logging

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query

from api.dependencies import get_dictionary_service
from api.schemas.dictionary import ContainsResponse
from api.schemas.dictionary import DictionaryContainsRequest
from api.schemas.dictionary import DictionarySearchRequest
from api.schemas.dictionary import ExactMatchResponse
from api.schemas.dictionary import SearchResponse
from api.schemas.dictionary import StatsResponse
from services.dictionary_service import DictionaryService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dictionary", tags=["Dictionary"])


@router.post("/search", response_model=SearchResponse)
def search_dictionary(
    request: DictionarySearchRequest,
    service: DictionaryService = Depends(get_dictionary_service)
):
    """Full-text search using FTS5."""
    try:
        return service.search_full_text(request)
    except Exception as e:
        logger.error("Dictionary search failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=e.args[0] if e.args else "Dictionary search failed"
        )


@router.get("/exact/{word}", response_model=ExactMatchResponse)
def get_exact_match(
    word: str,
    lang_from: str = Query(default="en"),
    lang_to: str = Query(default="de"),
    service: DictionaryService = Depends(get_dictionary_service)
):
    """Get exact translation for a specific word."""
    try:
        return service.search_exact_match(word, lang_from, lang_to)
    except Exception as e:
        logger.error("Exact match failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=e.args[0] if e.args else "Exact match failed"
        )


@router.post("/contains", response_model=ContainsResponse)
def search_contains(
    request: DictionaryContainsRequest,
    service: DictionaryService = Depends(get_dictionary_service)
):
    """Search for entries containing specific text (LIKE %text%)."""
    try:
        return service.search_contains(
            text=request.text,
            field=request.field,
            lang_from=request.lang_from,
            lang_to=request.lang_to,
            limit=request.limit
        )
    except ValueError as e:
        logger.warning("Invalid field parameter: %s", e)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Contains search failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=e.args[0] if e.args else "Contains search failed"
        )


@router.get("/stats", response_model=StatsResponse)
def get_stats(
    service: DictionaryService = Depends(get_dictionary_service)
):
    """Get statistics about the dictionary."""
    try:
        return service.get_stats()
    except Exception as e:
        logger.error("Stats retrieval failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=e.args[0] if e.args else "Stats retrieval failed"
        )
