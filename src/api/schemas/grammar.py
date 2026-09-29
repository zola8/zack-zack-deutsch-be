from pydantic import BaseModel
from pydantic import Field


class GrammarCheckRequest(BaseModel):
    """Request schema for grammar check endpoint."""
    text: str = Field(..., min_length=1, max_length=10000, description="Text to check")


class GrammarMatchContext(BaseModel):
    """Context around a grammar match."""
    text: str = Field(..., description="Surrounding text snippet")
    offset_in_context: int = Field(..., description="Offset of the error within the context")


class GrammarMatchRule(BaseModel):
    """Rule that triggered the grammar match."""
    id: str = Field(..., description="Rule identifier")
    category: str = Field(..., description="Rule category (e.g., 'CASING', 'GRAMMAR')")
    issue_type: str = Field(..., description="Type of issue (e.g., 'typographical', 'grammar')")


class GrammarMatch(BaseModel):
    """A single grammar issue found in the text."""
    message: str = Field(..., description="Description of the grammar issue")
    replacements: list[str] = Field(default_factory=list, description="Suggested corrections")
    offset: int = Field(..., description="Character offset where the issue starts")
    error_length: int = Field(..., description="Length of the problematic text")
    context: GrammarMatchContext = Field(..., description="Surrounding text context")
    rule: GrammarMatchRule = Field(..., description="Rule that triggered the match")
    sentence: str = Field(..., description="The full sentence containing the error")


class GrammarCheckResponse(BaseModel):
    """Response schema for grammar check endpoint."""
    text: str = Field(..., description="Original text that was checked")
    language: str = Field(..., description="Language used for checking")
    matches: list[GrammarMatch] = Field(default_factory=list, description="List of grammar issues found")
    match_count: int = Field(..., description="Total number of issues found")
    provider: str = Field(default="languagetool", description="Grammar checking provider used")
