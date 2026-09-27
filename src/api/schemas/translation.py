from typing import Any

from pydantic import BaseModel
from pydantic import Field


class TranslationRequest(BaseModel):
    """Request schema for translation endpoint."""
    text: str = Field(..., min_length=1, max_length=5000, description="Text to translate")
    source_lang: str = Field(default="DE", description="Source language code ('EN')")
    target_lang: str = Field(default="EN", description="Target language code ('DE')")
    options: dict[str, Any] | None = Field(
        default=None,
        description="Optional key-value pairs for translation settings"
    )


class TranslationResponse(BaseModel):
    """Response schema for translation endpoint."""
    translated_text: str = Field(..., description="Translated text")
    source_lang: str = Field(..., description="Source language code")
    target_lang: str = Field(..., description="Target language code")
    char_count: int = Field(..., description="Number of characters in original text")
