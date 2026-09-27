import logging

from services.translator.base import BaseTranslator
from services.translator.deepl_translator import DeepLTranslator
from services.translator.libre_translator import LibreTranslateTranslator

logger = logging.getLogger(__name__)


class TranslatorFactory:
    """Factory for creating translator instances."""

    _translators: dict[str, BaseTranslator] = {
        "deepl": DeepLTranslator(),
        "libre": LibreTranslateTranslator(),
    }

    @classmethod
    def get_translator(cls, provider: str) -> BaseTranslator:
        """
        Get a translator instance by provider name.

        Args:
            provider: Provider name (e.g., 'deepl', 'libre')

        Returns:
            Translator instance

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
