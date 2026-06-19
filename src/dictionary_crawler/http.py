import httpx

DEFAULT_HEADERS = {
    "Accept-Encoding": "gzip, deflate, br",
    "Upgrade-Insecure-Requests": "1",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Sec-Gpc": "1",
    "Accept-Language": "en-US,en;q=0.6",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    # TODO: Is this key required? If so, should it be randomized or static?
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
    "Sec-Fetch-Mode": "navigate",
}


def create_client(headers: dict[str, str] | None = None) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        headers=headers or DEFAULT_HEADERS,
        follow_redirects=True,
    )
