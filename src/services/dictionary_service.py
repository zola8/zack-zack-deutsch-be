import logging

from api.schemas.dictionary import ContainsResponse
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


class DictionaryService:
    """Service for handling dictionary operations."""

    def __init__(self, repo: DictionaryRepository):
        self.repo = repo

    def _to_entry_response(self, entry) -> DictionaryEntryResponse:
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

    def _to_search_result_response(self, result) -> SearchResultResponse:
        """Convert a persistence SearchResult to an API SearchResultResponse."""
        return SearchResultResponse(
            id=result.id,
            word_from=result.word_from,
            word_to=result.word_to,
            word_type=result.word_type,
            classification=result.classification,
            rank=result.rank,
        )

    def search_full_text(self, request: DictionarySearchRequest) -> SearchResponse:
        """Perform full-text search."""
        logger.debug(
            "Searching dictionary: query=%s, lang=%s->%s",
            request.query, request.lang_from, request.lang_to
        )

        results = self.repo.search_full_text(
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
            results=[self._to_search_result_response(r) for r in results]
        )

    def search_exact_match(self, word: str, lang_from: str, lang_to: str) -> ExactMatchResponse:
        """Get exact translation for a specific word."""
        logger.debug(
            "Searching exact match: word=%s, lang=%s->%s",
            word, lang_from, lang_to
        )

        results = self.repo.search_exact_match(
            word=word,
            lang_from=lang_from,
            lang_to=lang_to
        )

        logger.debug("Exact match completed: found %d results", len(results))

        return ExactMatchResponse(
            word=word,
            search_type="exact",
            count=len(results),
            translations=[self._to_entry_response(r) for r in results]
        )

    def search_contains(
        self,
        text: str,
        field: str,
        lang_from: str,
        lang_to: str,
        limit: int
    ) -> ContainsResponse:
        """Search for entries containing specific text (LIKE %text%)."""
        logger.debug(
            "Searching contains: text=%s, field=%s, lang=%s->%s",
            text, field, lang_from, lang_to
        )

        results = self.repo.search_contains(
            text=text,
            field=field,
            lang_from=lang_from,
            lang_to=lang_to,
            limit=limit
        )

        logger.debug("Contains search completed: found %d results", len(results))

        return ContainsResponse(
            search_text=text,
            search_field=field,
            search_type="contains",
            count=len(results),
            results=[self._to_entry_response(r) for r in results]
        )

    def get_stats(self) -> StatsResponse:
        """Get statistics about the dictionary."""
        logger.debug("Retrieving dictionary stats")

        stats = self.repo.get_stats()

        logger.debug("Stats retrieved successfully: %d total entries", stats.total_entries)

        return StatsResponse(
            total_entries=stats.total_entries,
            language_pairs=[
                LanguagePairStats(**lp) for lp in stats.language_pairs
            ],
            top_word_types=[
                WordTypeStats(**wt) for wt in stats.top_word_types
            ],
        )
