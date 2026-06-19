import pytest
import respx
import httpx

from dict_crawler.crawlers.cambridge import CambridgeCrawler
from dict_crawler.exceptions import (
    CambridgeFetchException,
    CambridgeParseException,
    CambridgeWordNotFoundException,
)
from dict_crawler.models.cambridge import (
    CambridgeSectionType,
    CambridgeSense,
)
from dict_crawler.models.common import CEFRLevel


BASE_URL = "https://dictionary.cambridge.org"


def load_fixture(name: str) -> str:
    from pathlib import Path
    return (Path(__file__).parent / "fixtures" / name).read_text()


@pytest.fixture
def crawler():
    return CambridgeCrawler()


@respx.mock
async def test_crawl_hello(crawler):
    html = load_fixture("hello_page.html")
    respx.get(f"{BASE_URL}/dictionary/english/hello").mock(
        return_value=httpx.Response(200, html=html)
    )
    page = await crawler.crawl("hello")

    assert page.search_term == "hello"
    assert len(page.sections) == 2

    american = page.sections[0]
    assert american.type == CambridgeSectionType.American
    assert len(american.entries) == 1
    entry = american.entries[0]
    assert entry.headword == "hello"
    assert entry.part_of_speech == "exclamation"
    assert entry.pronunciations is not None
    assert len(entry.pronunciations) == 1
    assert entry.pronunciations[0].region == "UK"
    assert entry.pronunciations[0].pronunciation == "/həˈləʊ/"
    assert len(entry.pronunciations[0].audio_urls) == 2
    assert entry.verb_forms is not None
    assert len(entry.verb_forms) == 1
    assert entry.verb_forms[0].form == "hellos"
    assert len(entry.senses) == 2
    assert entry.senses[0].cefr == CEFRLevel.A1
    assert entry.senses[1].cefr == CEFRLevel.B1

    first_sense = entry.senses[0]
    assert len(first_sense.definitions) == 1
    defn = first_sense.definitions[0]
    assert "greeting" in defn.definition.lower()
    assert defn.examples is not None
    assert len(defn.examples) == 2

    business = page.sections[1]
    assert business.type == CambridgeSectionType.Business


@respx.mock
async def test_crawl_examples(crawler):
    html = load_fixture("hello_page.html")
    respx.get(f"{BASE_URL}/dictionary/english/hello").mock(
        return_value=httpx.Response(200, html=html)
    )
    page = await crawler.crawl("hello")

    assert page.examples is not None
    assert len(page.examples) == 2
    assert "Hello, how are you?" in page.examples[0].example
    assert page.examples[0].source is not None
    assert page.examples[0].source.from_ == "BBC"
    assert page.examples[1].source is None


@respx.mock
async def test_crawl_collocations(crawler):
    html = load_fixture("hello_page.html")
    respx.get(f"{BASE_URL}/dictionary/english/hello").mock(
        return_value=httpx.Response(200, html=html)
    )
    page = await crawler.crawl("hello")

    assert page.collocations is not None
    assert len(page.collocations) == 1
    assert page.collocations[0].collocation == "say hello"
    assert "said hello" in page.collocations[0].example


@respx.mock
async def test_word_not_found(crawler):
    respx.get(f"{BASE_URL}/dictionary/english/xyznotaword").mock(
        return_value=httpx.Response(404)
    )
    with pytest.raises(CambridgeWordNotFoundException) as exc_info:
        await crawler.crawl("xyznotaword")
    assert exc_info.value.word == "xyznotaword"


@respx.mock
async def test_server_error(crawler):
    respx.get(f"{BASE_URL}/dictionary/english/hello").mock(
        return_value=httpx.Response(500)
    )
    with pytest.raises(CambridgeFetchException) as exc_info:
        await crawler.crawl("hello")
    assert exc_info.value.status_code == 500


@respx.mock
async def test_empty_body(crawler):
    respx.get(f"{BASE_URL}/dictionary/english/hello").mock(
        return_value=httpx.Response(200, text="")
    )
    with pytest.raises(CambridgeFetchException) as exc_info:
        await crawler.crawl("hello")
    assert "Empty" in str(exc_info.value)


@respx.mock
async def test_empty_collocations_dataset(crawler):
    html = load_fixture("hello_page.html")
    # Remove collocations section
    html = html.replace('<div id="dataset_combinations">', '<div id="no-combos">')
    respx.get(f"{BASE_URL}/dictionary/english/hello").mock(
        return_value=httpx.Response(200, html=html)
    )
    page = await crawler.crawl("hello")
    assert page.collocations is None


@respx.mock
async def test_empty_examples_dataset(crawler):
    html = load_fixture("hello_page.html")
    html = html.replace('id="dataset-example"', 'id="no-examples"')
    respx.get(f"{BASE_URL}/dictionary/english/hello").mock(
        return_value=httpx.Response(200, html=html)
    )
    page = await crawler.crawl("hello")
    assert page.examples is None


def test_get_url():
    crawler = CambridgeCrawler()
    url = crawler._get_url("hello")
    assert url == f"{BASE_URL}/dictionary/english/hello"


def test_get_media_url():
    crawler = CambridgeCrawler()
    url = crawler._get_media_url("/dictionary/english/media/hello.mp3")
    assert url == f"{BASE_URL}/dictionary/english/media/hello.mp3"
