from typing import Callable

from dominate.dom_tag import dom_tag
from dominate.tags import html_tag


RenderResult = html_tag | dom_tag
RenderFunction = Callable[[...], RenderResult]
