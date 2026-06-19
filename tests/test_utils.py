from dict_crawler.utils import generate_link


def test_generate_link_basic():
    result = generate_link("https://dictionary.cambridge.org", "/dictionary/english/hello")
    assert result == "https://dictionary.cambridge.org/dictionary/english/hello"


def test_generate_link_encodes_special_chars():
    result = generate_link("https://example.com", "/path/hello world")
    assert "hello%20world" in result or "hello+world" in result


def test_generate_link_base_url_with_trailing_slash():
    result = generate_link("https://example.com/", "/path/to")
    assert result == "https://example.com/path/to"


def test_generate_link_no_leading_slash():
    result = generate_link("https://example.com", "dictionary/english/hello")
    assert "dictionary/english/hello" in result
