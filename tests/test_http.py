import httpx

from dict_crawler.http import DEFAULT_HEADERS, create_client


def test_create_client_returns_async_client():
    client = create_client()
    assert isinstance(client, httpx.AsyncClient)
    assert client.is_closed is False


def test_create_client_follows_redirects():
    client = create_client()
    assert client.follow_redirects is True


def test_create_client_default_headers():
    client = create_client()
    for key, value in DEFAULT_HEADERS.items():
        assert client.headers[key] == value


def test_create_client_custom_headers():
    custom = {"X-Custom": "test"}
    client = create_client(headers=custom)
    assert client.headers["X-Custom"] == "test"
