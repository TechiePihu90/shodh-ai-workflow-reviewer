
from typing import Any, Protocol


class ModelClient(Protocol):
    """Interface for AI model clients."""

    def review(self, prompt: str) -> dict[str, Any]:
        ...


class FakeModelClient:
    """Fake AI client for testing without paid API access."""

    def __init__(self, response: dict[str, Any] | None = None):
        self.response = response or {
            "status": "PASS",
            "findings": [],
            "summary": "No issues detected by the fake model."
        }

    def review(self, prompt: str) -> dict[str, Any]:
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        return self.response.copy()
