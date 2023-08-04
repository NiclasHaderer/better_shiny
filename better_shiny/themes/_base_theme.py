import functools

import httpx
from dominate.tags import style
from dominate.util import raw
from httpx._types import URLTypes


@functools.lru_cache(maxsize=100)
def fetch_text(url: URLTypes) -> str:
    response = httpx.get(url)
    response.raise_for_status()
    return response.text


def theme_factory(theme_url: URLTypes) -> style:
    style_sheet = fetch_text(theme_url)
    return style(raw(style_sheet))
