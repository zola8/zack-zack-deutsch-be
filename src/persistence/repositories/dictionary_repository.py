import sqlite3

from persistence.models.dictionary_models import DictionaryEntry
from persistence.models.dictionary_models import SearchResult
from persistence.models.dictionary_models import StatsResult


class DictionaryRepository:
    def __init__(self, db_path: str):
        import os
        if not os.path.exists(db_path):
            raise ValueError(f"Database file not found: {db_path}")

        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        """Create a read-only, immutable connection."""
        conn = sqlite3.connect(
            f"file:{self.db_path}?mode=ro&immutable=1",
            uri=True
        )
        conn.row_factory = sqlite3.Row
        return conn

    def _row_to_entry(self, row: sqlite3.Row) -> DictionaryEntry:
        """Convert a database row to a DictionaryEntry model."""
        return DictionaryEntry(
            id=row["id"],
            word_from=row["word_from"],
            word_to=row["word_to"],
            word_type=row["word_type"],
            classification=row["classification"],
            lang_from=row["lang_from"],
            lang_to=row["lang_to"],
        )

    def _row_to_search_result(self, row: sqlite3.Row) -> SearchResult:
        """Convert a database row to a SearchResult model."""
        return SearchResult(
            id=row["id"],
            word_from=row["word_from"],
            word_to=row["word_to"],
            word_type=row["word_type"],
            classification=row["classification"],
            rank=row["rank"] if "rank" in row.keys() else None,
        )

    def search_full_text(
        self,
        query: str,
        lang_from: str = "en",
        lang_to: str = "de",
        limit: int = 50
    ) -> list[SearchResult]:
        """Full-text search using FTS5."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            fts_query = query if query.endswith('*') else f"{query}*"

            cursor.execute("""
                SELECT e.id, e.word_from, e.word_to, e.word_type, 
                       e.classification, rank
                FROM dictionary_fts fts
                JOIN dictionary_entries e ON e.id = fts.rowid
                WHERE dictionary_fts MATCH ?
                  AND e.lang_from = ?
                  AND e.lang_to = ?
                ORDER BY rank
                LIMIT ?
            """, (fts_query, lang_from, lang_to, limit))

            return [self._row_to_search_result(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def search_exact_match(
        self,
        word: str,
        lang_from: str = "en",
        lang_to: str = "de"
    ) -> list[DictionaryEntry]:
        """Get exact translation for a word."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, word_from, word_to, word_type, classification,
                       lang_from, lang_to
                FROM dictionary_entries
                WHERE word_from = ?
                  AND lang_from = ?
                  AND lang_to = ?
            """, (word, lang_from, lang_to))

            return [self._row_to_entry(row) for row in cursor.fetchall()]
        finally:
            conn.close()

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

        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT id, word_from, word_to, word_type, classification,
                       lang_from, lang_to
                FROM dictionary_entries
                WHERE {field} LIKE ? COLLATE NOCASE
                  AND lang_from = ?
                  AND lang_to = ?
                LIMIT ?
            """, (f"%{text}%", lang_from, lang_to, limit))

            return [self._row_to_entry(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def search_by_type(
        self,
        word_type: str,
        lang_from: str = "en",
        lang_to: str = "de",
        limit: int = 50
    ) -> list[DictionaryEntry]:
        """Get all entries of a specific word type."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, word_from, word_to, word_type, classification,
                       lang_from, lang_to
                FROM dictionary_entries
                WHERE word_type = ?
                  AND lang_from = ?
                  AND lang_to = ?
                LIMIT ?
            """, (word_type, lang_from, lang_to, limit))

            return [self._row_to_entry(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_stats(self) -> StatsResult:
        """Get dictionary statistics."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) as total FROM dictionary_entries")
            total = cursor.fetchone()["total"]

            cursor.execute("""
                SELECT lang_from, lang_to, COUNT(*) as count
                FROM dictionary_entries
                GROUP BY lang_from, lang_to
                ORDER BY count DESC
            """)
            languages = [dict(row) for row in cursor.fetchall()]

            cursor.execute("""
                SELECT word_type, COUNT(*) as count
                FROM dictionary_entries
                WHERE word_type IS NOT NULL
                GROUP BY word_type
                ORDER BY count DESC
                LIMIT 20
            """)
            word_types = [dict(row) for row in cursor.fetchall()]

            return StatsResult(
                total_entries=total,
                language_pairs=languages,
                top_word_types=word_types
            )
        finally:
            conn.close()
