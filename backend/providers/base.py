"""Provider abstraction layer for Decision Workbench.

Each provider implements a uniform async interface so the rest of the system
never touches provider-specific details. A mock provider ships by default so
the full divergence -> map -> human-decision loop runs with zero API keys;
real providers (OpenRouter) can be added as drop-in files.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class ProviderError(Exception):
    """Raised when a provider fails to produce a response."""


class BaseProvider(ABC):
    """Interface every provider must implement."""

    name: str = "base"

    @abstractmethod
    async def query(
        self,
        model: str,
        messages: List[Dict[str, str]],
        timeout: float = 60.0,
    ) -> Optional[Dict[str, Any]]:
        """Send a chat completion request.

        Args:
            model: Model identifier (provider-specific).
            messages: OpenAI-style message list [{"role": ..., "content": ...}].
            timeout: Request timeout in seconds.

        Returns:
            Dict with at least {'content': str} on success, or None on failure.
        """
        raise NotImplementedError

    def list_models(self) -> List[str]:
        """Return available model identifiers for this provider."""
        return []


class ProviderRegistry:
    """Maps provider names to provider instances."""

    def __init__(self) -> None:
        self._providers: Dict[str, BaseProvider] = {}
        self._default: Optional[str] = None

    def register(self, provider: BaseProvider, *, make_default: bool = False) -> None:
        self._providers[provider.name] = provider
        if make_default or self._default is None:
            self._default = provider.name

    def get(self, name: Optional[str] = None) -> BaseProvider:
        if name is None:
            name = self._default
        if name is None or name not in self._providers:
            raise ProviderError(
                f"Unknown provider: {name!r}. Available: {list(self._providers)}"
            )
        return self._providers[name]

    def list(self) -> Dict[str, List[str]]:
        return {name: p.list_models() for name, p in self._providers.items()}
