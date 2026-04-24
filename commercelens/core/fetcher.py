from __future__ import annotations

import httpx

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (compatible; CommerceLens/0.1; +https://github.com/dipeshbabu/commerce-lens)"
)


class FetchError(RuntimeError):
    """Raised when CommerceLens cannot fetch a URL."""


async def fetch_html_async(url: str, timeout: float = 20.0) -> str:
    headers = {"User-Agent": DEFAULT_USER_AGENT}
    async with httpx.AsyncClient(follow_redirects=True, timeout=timeout, headers=headers) as client:
        response = await client.get(url)
        if response.status_code >= 400:
            raise FetchError(f"Failed to fetch {url}: HTTP {response.status_code}")
        return response.text


def fetch_html(url: str, timeout: float = 20.0) -> str:
    headers = {"User-Agent": DEFAULT_USER_AGENT}
    with httpx.Client(follow_redirects=True, timeout=timeout, headers=headers) as client:
        response = client.get(url)
        if response.status_code >= 400:
            raise FetchError(f"Failed to fetch {url}: HTTP {response.status_code}")
        return response.text
