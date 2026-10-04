import logging

from persistence.models.dictionary_models import DictionaryEntry
from persistence.models.dictionary_models import SearchResult
from persistence.models.dictionary_models import StatsResult

logger = logging.getLogger(__name__)


class DictionaryRepository:
    def __init__(self, conn):
        """Initialize with an active libsql/Turso connection."""
        self.conn = conn

    def _row_to_entry(self, row) -> DictionaryEntry:
        """Convert a database row to a DictionaryEntry model."""
        return DictionaryEntry(
            id=row[0],
            word_from=row[1],
            word_to=row[2],
            word_type=row[3],
            classification=row[4],
            lang_from=row[5],
            lang_to=row[6],
        )

    def _row_to_search_result(self, row) -> SearchResult:
        """Convert a database row to a SearchResult model."""
        return SearchResult(
            id=row[0],
            word_from=row[1],
            word_to=row[2],
            word_type=row[3],
            classification=row[4],
            rank=row[5] if len(row) > 5 else None,
        )

    def search_full_text(self, query: str, lang_from: str = "en", lang_to: str = "de", limit: int = 50) -> list[
        SearchResult]:
        fts_query = query if query.endswith('*') else f"{query}*"

        cursor = self.conn.execute("""
            SELECT e.id, e.word_from, e.word_to, e.word_type, 
                   e.classification, rank
            FROM dictionary_fts fts
            JOIN dictionary_entries e ON e.id = fts.rowid
            WHERE dictionary_fts MATCH ?
              AND e.lang_from = ?
              AND e.lang_to = ?
            ORDER BY rank
            LIMIT ?
        """, [fts_query, lang_from, lang_to, limit])

        return [self._row_to_search_result(row) for row in cursor.fetchall()]

    def search_exact_match(self, word: str, lang_from: str = "en", lang_to: str = "de") -> list[DictionaryEntry]:
        cursor = self.conn.execute("""
            SELECT id, word_from, word_to, word_type, classification, lang_from, lang_to
            FROM dictionary_entries
            WHERE word_from = ? AND lang_from = ? AND lang_to = ?
        """, [word, lang_from, lang_to])

        return [self._row_to_entry(row) for row in cursor.fetchall()]

    def search_contains(
        self,
        text: str,
        field: str = "word_from",
        lang_from: str = "en",
        lang_to: str = "de",
        limit: int = 50
    ) -> list[DictionaryEntry]:
        """Search for entries containing text (LIKE %text%)."""
        if field not in ["word_from", "word_to", "classification"]:
            raise ValueError(f"Invalid field: {field}")

        cursor = self.conn.execute(f"""
            SELECT id, word_from, word_to, word_type, classification,
                   lang_from, lang_to
            FROM dictionary_entries
            WHERE {field} LIKE ? COLLATE NOCASE
              AND lang_from = ?
              AND lang_to = ?
            LIMIT ?
        """, [f"%{text}%", lang_from, lang_to, limit])

        return [self._row_to_entry(row) for row in cursor.fetchall()]

    def get_stats(self) -> StatsResult:
        """Get dictionary statistics."""
        # Total entries
        total_row = self.conn.execute("SELECT COUNT(*) as total FROM dictionary_entries").fetchone()
        total = total_row[0]

        # Language pairs
        lang_cursor = self.conn.execute("""
            SELECT lang_from, lang_to, COUNT(*) as count
            FROM dictionary_entries
            GROUP BY lang_from, lang_to
            ORDER BY count DESC
        """)
        languages = [{"lang_from": row[0], "lang_to": row[1], "count": row[2]} for row in lang_cursor.fetchall()]

        # Top word types
        type_cursor = self.conn.execute("""
            SELECT word_type, COUNT(*) as count
            FROM dictionary_entries
            WHERE word_type IS NOT NULL
            GROUP BY word_type
            ORDER BY count DESC
            LIMIT 20
        """)
        word_types = [{"word_type": row[0], "count": row[1]} for row in type_cursor.fetchall()]

        return StatsResult(
            total_entries=total,
            language_pairs=languages,
            top_word_types=word_types
        )
