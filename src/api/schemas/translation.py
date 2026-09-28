from typing import Any

from pydantic import BaseModel
from pydantic import Field


class TranslationRequest(BaseModel):
    """Request schema for translation endpoint."""
    text: str = Field(..., min_length=1, max_length=5000, description="Text to translate")
    source_lang: str = Field(default="EN", description="Source language code ('DE', 'EN')")
    target_lang: str = Field(default="DE", description="Target language code ('EN', 'DE')")
    provider: str = Field(
        default="azure",
        description="Translation provider to use"
    )
    options: dict[str, Any] | None = Field(
        default=None,
        description="Optional provider-specific settings"
    )


class TranslationResponse(BaseModel):
    """Response schema for translation endpoint."""
    translated_text: str = Field(..., description="Translated text")
    source_lang: str = Field(..., description="Source language code")
    target_lang: str = Field(..., description="Target language code")
    char_count: int = Field(..., description="Number of characters in original text")
    provider: str = Field(..., description="Translation provider used")
    metadata: dict[str, Any] | None = Field(
        default=None,
        description="Additional provider-specific data not covered by typed fields"
    )
