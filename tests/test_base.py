import httpx
import pytest

from dict_crawler.base import BaseCrawler
from dict_crawler.http import create_client


class DummyCrawler(BaseCrawler):
    async def crawl(self, word: str):
        return f"fetched {word}"


async def test_base_crawler_uses_provided_client():
    client = create_client()
    crawler = DummyCrawler(client=client)
    assert crawler._client is client


async def test_base_crawler_creates_default_client():
    crawler = DummyCrawler()
    assert isinstance(crawler._client, httpx.AsyncClient)


async def test_base_crawler_crawl_is_abstract():
    with pytest.raises(TypeError):
        BaseCrawler()


async def test_subclass_crawl():
    crawler = DummyCrawler()
    result = await crawler.crawl("hello")
    assert result == "fetched hello"


async def test_aenter_returns_self():
    crawler = DummyCrawler()
    async with crawler as c:
        assert c is crawler


async def test_aexit_closes_client():
    client = create_client()
    crawler = DummyCrawler(client=client)
    async with crawler:
        assert not client.is_closed
    assert client.is_closed


async def test_aexit_closes_default_client():
    async with DummyCrawler() as crawler:
        assert not crawler._client.is_closed
    assert crawler._client.is_closed
