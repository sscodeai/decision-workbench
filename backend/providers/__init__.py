"""Provider registry wiring for Decision Workbench.

Selects the active provider based on config. Defaults to the mock provider so
the full loop runs with no API keys. To use a real provider, add it here and
set PROVIDER=openrouter in the environment.
"""

from .base import BaseProvider, ProviderError, ProviderRegistry  # noqa: F401
from .mock import MockProvider

_registry: ProviderRegistry = None  # type: ignore


def get_registry() -> ProviderRegistry:
    """Build (once) and return the global provider registry."""
    global _registry
    if _registry is None:
        _registry = ProviderRegistry()
        _registry.register(MockProvider(), make_default=True)
        try:
            from .openrouter import OpenRouterProvider
            from ..config import OPENROUTER_API_KEY, OPENROUTER_API_URL, OPENROUTER_MODEL

            if OPENROUTER_API_KEY:
                _registry.register(
                    OpenRouterProvider(
                        api_key=OPENROUTER_API_KEY,
                        api_url=OPENROUTER_API_URL,
                        default_model=OPENROUTER_MODEL,
                    )
                )
        except Exception as exc:  # noqa: BLE001 — registry must not fail on optional provider
            print(f"[providers] openrouter not registered: {exc}")
    return _registry


def get_provider(name: str | None = None) -> BaseProvider:
    """Return the active provider instance."""
    return get_registry().get(name)


__all__ = [
    "BaseProvider",
    "ProviderRegistry",
    "ProviderError",
    "MockProvider",
    "get_registry",
    "get_provider",
]
