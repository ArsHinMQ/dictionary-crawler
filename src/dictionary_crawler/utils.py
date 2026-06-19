from urllib.parse import urljoin, quote


def generate_link(base_url: str, route: str) -> str:
    return urljoin(base_url, quote(route))
