import pytest

from dict_crawler.exceptions import (
    CambridgeException,
    CambridgeFetchException,
    CambridgeParseException,
    CambridgeWordNotFoundException,
    DictionaryException,
    DictionaryFetchException,
    DictionaryParseException,
    DictionaryWordNotFoundException,
)


def test_hierarchy():
    assert issubclass(DictionaryFetchException, DictionaryException)
    assert issubclass(DictionaryWordNotFoundException, DictionaryException)
    assert issubclass(DictionaryParseException, DictionaryException)
    assert issubclass(CambridgeException, DictionaryException)
    assert issubclass(CambridgeFetchException, DictionaryFetchException)
    assert issubclass(CambridgeFetchException, CambridgeException)
    assert issubclass(CambridgeWordNotFoundException, DictionaryWordNotFoundException)
    assert issubclass(CambridgeWordNotFoundException, CambridgeException)
    assert issubclass(CambridgeParseException, DictionaryParseException)
    assert issubclass(CambridgeParseException, CambridgeException)


def test_fetch_exception_attrs():
    e = CambridgeFetchException("failed", url="https://example.com", status_code=500)
    assert e.url == "https://example.com"
    assert e.status_code == 500
    assert "failed" in str(e)


def test_fetch_exception_default_message():
    e = CambridgeFetchException(url="https://example.com", status_code=404)
    msg = str(e)
    assert "404" in msg
    assert "https://example.com" in msg


def test_word_not_found_exception():
    e = CambridgeWordNotFoundException("xyznotaword")
    assert e.word == "xyznotaword"
    assert "xyznotaword" in str(e)


def test_parse_exception():
    e = CambridgeParseException("bad html", word="hello", detail="missing div")
    assert e.word == "hello"
    assert e.detail == "missing div"
    assert "bad html" in str(e)


def test_parse_exception_default_message():
    e = CambridgeParseException(word="hello", detail="missing div")
    msg = str(e)
    assert "hello" in msg
    assert "missing div" in msg
