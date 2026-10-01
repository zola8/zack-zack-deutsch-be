from typing import Optional

from pydantic import BaseModel


class DictionaryEntry(BaseModel):
    id: int
    word_from: str
    word_to: str
    word_type: Optional[str] = None
    classification: Optional[str] = None
    lang_from: str
    lang_to: str


class SearchResult(BaseModel):
    id: int
    word_from: str
    word_to: str
    word_type: Optional[str] = None
    classification: Optional[str] = None
    rank: Optional[float] = None


class StatsResult(BaseModel):
    total_entries: int
    language_pairs: list[dict]
    top_word_types: list[dict]
