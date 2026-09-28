import logging

from services.translator.azure_translator import AzureTranslator
from services.translator.base import BaseTranslator
from services.translator.deepl_translator import DeepLTranslator

logger = logging.getLogger(__name__)


class TranslatorFactory:
    """Factory for creating translator instances."""

    _translators: dict[str, BaseTranslator] = {
        "deepl": DeepLTranslator(),
        "azure": AzureTranslator(),
    }

    @classmethod
    def get_translator(cls, provider: str) -> BaseTranslator:
        """
        Get a translator instance by provider name.

        Raises:
            ValueError: If provider is not supported
        """
        translator = cls._translators.get(provider.lower())
        if not translator:
            available = ", ".join(cls._translators.keys())
            raise ValueError(f"Unsupported provider '{provider}'. Available: {available}")

        return translator

    @classmethod
    def get_available_providers(cls) -> list[str]:
        """Return list of available provider names."""
        return list(cls._translators.keys())
