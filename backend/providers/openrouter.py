"""OpenRouter provider for Decision Workbench.

Routes model queries through OpenRouter's OpenAI-compatible chat completions
endpoint. Requires OPENROUTER_API_KEY.
"""

import httpx
from typing import Any, Dict, List, Optional

from .base import BaseProvider


class OpenRouterProvider(BaseProvider):
    """Real LLM provider via OpenRouter."""

    name = "openrouter"

    def __init__(
        self,
        api_key: str,
        api_url: str = "https://openrouter.ai/api/v1/chat/completions",
        default_model: str = "anthropic/claude-3.5-sonnet",
    ) -> None:
        self.api_key = api_key
        self.api_url = api_url
        self.default_model = default_model

    async def query(
        self,
        model: str,
        messages: List[Dict[str, str]],
        timeout: float = 120.0,
    ) -> Optional[Dict[str, Any]]:
        if not self.api_key:
            return None
        model_id = model if model and model.startswith(("anthropic/", "openai/", "google/", "deepseek/", "meta-")) else self.default_model
        payload = {
            "model": model_id,
            "messages": messages,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(self.api_url, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
            content = data["choices"][0]["message"]["content"]
            return {"content": content}
        except Exception as exc:  # noqa: BLE001 — provider boundary, log and degrade
            print(f"[openrouter] error querying {model}: {exc}")
            return None

    def list_models(self) -> List[str]:
        return [self.default_model]
