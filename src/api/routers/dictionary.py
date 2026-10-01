import logging

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query

from api.dependencies import get_dictionary_repo
from api.schemas.dictionary import ByTypeResponse
from api.schemas.dictionary import ContainsResponse
from api.schemas.dictionary import DictionaryContainsRequest
from api.schemas.dictionary import DictionaryEntryResponse
from api.schemas.dictionary import DictionarySearchRequest
from api.schemas.dictionary import ExactMatchResponse
from api.schemas.dictionary import LanguagePairStats
from api.schemas.dictionary import SearchResponse
from api.schemas.dictionary import SearchResultResponse
from api.schemas.dictionary import StatsResponse
from api.schemas.dictionary import WordTypeStats
from persistence.repositories.dictionary_repository import DictionaryRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dictionary", tags=["Dictionary"])


# ============================================================================
# Helper conversion functions
# ============================================================================
def _to_entry_response(entry) -> DictionaryEntryResponse:
    """Convert a persistence DictionaryEntry to an API DictionaryEntryResponse."""
    return DictionaryEntryResponse(
        id=entry.id,
        word_from=entry.word_from,
        word_to=entry.word_to,
        word_type=entry.word_type,
        classification=entry.classification,
        lang_from=entry.lang_from,
        lang_to=entry.lang_to,
    )


def _to_search_result_response(result) -> SearchResultResponse:
    """Convert a persistence SearchResult to an API SearchResultResponse."""
    return SearchResultResponse(
        id=result.id,
        word_from=result.word_from,
        word_to=result.word_to,
        word_type=result.word_type,
        classification=result.classification,
        rank=result.rank,
    )


# ============================================================================
# Endpoints
# ============================================================================
@router.post("/search", response_model=SearchResponse)
async def search_dictionary(
    request: DictionarySearchRequest,
    repo: DictionaryRepository = Depends(get_dictionary_repo)
):
    """Full-text search using FTS5."""
    logger.debug("Received dictionary search request: query=%s, lang=%s->%s",
                 request.query, request.lang_from, request.lang_to)

    try:
        results = repo.search_full_text(
            query=request.query,
            lang_from=request.lang_from,
            lang_to=request.lang_to,
            limit=request.limit
        )

        logger.debug("Search completed: found %d results", len(results))

        return SearchResponse(
            query=request.query,
            search_type="full-text",
            lang_from=request.lang_from,
            lang_to=request.lang_to,
            count=len(results),
            results=[_to_search_result_response(r) for r in results]
        )
    except Exception as e:
        logger.error("Dictionary search failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=e.args[0] if e.args else "Dictionary search failed"
        )


@router.get("/exact/{word}", response_model=ExactMatchResponse)
async def get_exact_match(
    word: str,
    lang_from: str = Query(default="en"),
    lang_to: str = Query(default="de"),
    repo: DictionaryRepository = Depends(get_dictionary_repo)
):
    """Get exact translation for a specific word."""
    logger.debug("Received exact match request: word=%s, lang=%s->%s",
                 word, lang_from, lang_to)

    try:
        results = repo.search_exact_match(
            word=word,
            lang_from=lang_from,
            lang_to=lang_to
        )

        logger.debug("Exact match completed: found %d results", len(results))

        return ExactMatchResponse(
            word=word,
            search_type="exact",
            count=len(results),
            translations=[_to_entry_response(r) for r in results]
        )
    except Exception as e:
        logger.error("Exact match failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=e.args[0] if e.args else "Exact match failed"
        )


@router.post("/contains", response_model=ContainsResponse)
async def search_contains(
    request: DictionaryContainsRequest,
    repo: DictionaryRepository = Depends(get_dictionary_repo)
):
    """Search for entries containing specific text (LIKE %text%)."""
    logger.debug("Received contains request: text=%s, field=%s, lang=%s->%s",
                 request.text, request.field, request.lang_from, request.lang_to)

    try:
        results = repo.search_contains(
            text=request.text,
            field=request.field,
            lang_from=request.lang_from,
            lang_to=request.lang_to,
            limit=request.limit
        )

        logger.debug("Contains search completed: found %d results", len(results))

        return ContainsResponse(
            search_text=request.text,
            search_field=request.field,
            search_type="contains",
            count=len(results),
            results=[_to_entry_response(r) for r in results]
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


@router.get("/by-type/{word_type}", response_model=ByTypeResponse)
async def search_by_type(
    word_type: str,
    lang_from: str = Query(default="en"),
    lang_to: str = Query(default="de"),
    limit: int = Query(default=50, ge=1, le=200),
    repo: DictionaryRepository = Depends(get_dictionary_repo)
):
    """Get all entries of a specific word type."""
    logger.debug("Received by-type request: type=%s, lang=%s->%s",
                 word_type, lang_from, lang_to)

    try:
        results = repo.search_by_type(
            word_type=word_type,
            lang_from=lang_from,
            lang_to=lang_to,
            limit=limit
        )

        logger.debug("By-type search completed: found %d results", len(results))

        return ByTypeResponse(
            word_type=word_type,
            search_type="by_type",
            count=len(results),
            results=[_to_entry_response(r) for r in results]
        )
    except Exception as e:
        logger.error("By-type search failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=e.args[0] if e.args else "By-type search failed"
        )


@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    repo: DictionaryRepository = Depends(get_dictionary_repo)
):
    """Get statistics about the dictionary."""
    logger.debug("Received stats request")

    try:
        stats = repo.get_stats()

        logger.debug("Stats retrieved successfully: %d total entries", stats.total_entries)

        # Convert the nested dicts/lists to proper API response models
        return StatsResponse(
            total_entries=stats.total_entries,
            language_pairs=[
                LanguagePairStats(**lp) for lp in stats.language_pairs
            ],
            top_word_types=[
                WordTypeStats(**wt) for wt in stats.top_word_types
            ],
        )
    except Exception as e:
        logger.error("Stats retrieval failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=e.args[0] if e.args else "Stats retrieval failed"
        )
