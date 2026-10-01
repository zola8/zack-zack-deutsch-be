from typing import Optional

from pydantic import BaseModel
from pydantic import Field


class DictionarySearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search term")
    lang_from: str = Field(default="en", description="Source language code")
    lang_to: str = Field(default="de", description="Target language code")
    limit: int = Field(default=50, ge=1, le=200, description="Maximum results")


class DictionaryContainsRequest(BaseModel):
    text: str = Field(..., min_length=2, description="Text to search for")
    field: str = Field(default="word_from", description="Field to search: word_from, word_to, or classification")
    lang_from: str = Field(default="en")
    lang_to: str = Field(default="de")
    limit: int = Field(default=50, ge=1, le=200)


class DictionaryEntryResponse(BaseModel):
    id: int
    word_from: str
    word_to: str
    word_type: Optional[str] = None
    classification: Optional[str] = None
    lang_from: str
    lang_to: str


class SearchResultResponse(BaseModel):
    id: int
    word_from: str
    word_to: str
    word_type: Optional[str] = None
    classification: Optional[str] = None
    rank: Optional[float] = None


class SearchResponse(BaseModel):
    query: str
    search_type: str
    lang_from: str
    lang_to: str
    count: int
    results: list[SearchResultResponse]


class ContainsResponse(BaseModel):
    search_text: str
    search_field: str
    search_type: str
    count: int
    results: list[DictionaryEntryResponse]


class ExactMatchResponse(BaseModel):
    word: str
    search_type: str
    count: int
    translations: list[DictionaryEntryResponse]


class ByTypeResponse(BaseModel):
    word_type: str
    search_type: str
    count: int
    results: list[DictionaryEntryResponse]


class LanguagePairStats(BaseModel):
    lang_from: str
    lang_to: str
    count: int


class WordTypeStats(BaseModel):
    word_type: str
    count: int


class StatsResponse(BaseModel):
    total_entries: int
    language_pairs: list[LanguagePairStats]
    top_word_types: list[WordTypeStats]
