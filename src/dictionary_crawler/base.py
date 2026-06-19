from abc import ABC, abstractmethod

import httpx

from dictionary_crawler.http import create_client


class BaseCrawler(ABC):
    def __init__(self, client: httpx.AsyncClient | None = None):
        self._client = client or create_client()
        self._owns_client = client is None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._owns_client:
            await self._client.aclose()
        return False

    def __del__(self):
        if self._owns_client and self._client and not self._client.is_closed:
            import warnings

            warnings.warn(
                f"{type(self).__name__} was not used as a context manager. "
                f"Use `async with {type(self).__name__}() as crawler:` to ensure cleanup.",
                ResourceWarning,
                source=self,
            )

    @abstractmethod
    async def crawl(self, word: str):
        ...
