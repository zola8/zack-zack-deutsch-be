from abc import ABC
from abc import abstractmethod

from api.schemas.translation import TranslationRequest
from api.schemas.translation import TranslationResponse


class BaseTranslator(ABC):
    """Abstract base class for all translation providers."""

    @abstractmethod
    async def translate(self, request: TranslationRequest) -> TranslationResponse:
        """
        Translate text using this provider.

        Args:
            request: Translation request with text, languages, and provider-specific options

        Returns:
            TranslationResponse with translated text
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the name of this translation provider."""
        pass
