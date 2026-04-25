from __future__ import annotations

from urllib.parse import urldefrag, urljoin, urlparse, urlunparse


def normalize_url(url: str, base_url: str | None = None) -> str:
    absolute = urljoin(base_url or "", url)
    absolute, _fragment = urldefrag(absolute)
    parsed = urlparse(absolute)
    scheme = parsed.scheme.lower() or "https"
    netloc = parsed.netloc.lower()
    path = _collapse_adjacent_duplicate_segments(parsed.path or "/")
    return urlunparse((scheme, netloc, path, "", parsed.query, ""))


def same_domain(url: str, other_url: str) -> bool:
    return urlparse(url).netloc.lower() == urlparse(other_url).netloc.lower()


def _collapse_adjacent_duplicate_segments(path: str) -> str:
    parts = path.split("/")
    collapsed: list[str] = []
    for part in parts:
        if part and collapsed and collapsed[-1] == part:
            continue
        collapsed.append(part)
    return "/".join(collapsed) or "/"
