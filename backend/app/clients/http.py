from typing import Any

import requests


class JsonHttpClient:
    """Tiny JSON client with one place for timeouts and error handling."""

    def __init__(self, timeout_seconds: float, user_agent: str) -> None:
        self.timeout_seconds = timeout_seconds
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent, "Accept": "application/json"})

    def get(self, url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        response = self.session.get(
            url,
            params=params,
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        return response.json()
