from typing import Iterator, Tuple

import dominate.tags
from dominate import document
from dominate.tags import meta, script, head as dominate_head
from starlette.responses import HTMLResponse

from better_shiny._types import RenderResult


class DominatorResponse(HTMLResponse):
    def render(self, content: RenderResult | Tuple[dominate_head, RenderResult]) -> bytes:
        """
        Render the content of the response.
        :param content: Two different types are supported:
            1. A RenderResult object, which is the root of the html document (if the html element is not a
            document, it will be wrapped in a document object).
            2. A tuple of two dominate objects, where the first is of type head and the second one of type RenderResult.
        :return:
        """

        # If the content is a tuple, the first element is the head and the second is the document
        if isinstance(content, tuple) and len(content) == 2 or isinstance(content, list) and len(content) == 2:
            head = content[0]
            content = content[1]

            if not isinstance(head, dominate_head):
                raise TypeError(f"App handler returned {type(head)} for head instead of tuple[head, RenderResult].")

            if not isinstance(content, RenderResult):
                raise TypeError(
                    f"App handler returned {type(content)} for document instead of tuple[head, RenderResult]."
                )
        elif isinstance(content, RenderResult):
            # If the content is a "RenderResult", we do not have a head
            head = None
        else:
            raise TypeError(
                f"App handler returned {type(content)} instead of RenderResult or tuple[head, RenderResult]."
            )

        # If the content is not a document, we wrap it in a document
        if not isinstance(content, document):
            doc = document()
            doc.head.remove(doc.title_node)
            doc.body += content
        else:
            doc = content

        # If we have a custom head, replace the default head of the dominate html document
        if head is not None:
            doc.head.clear()
            doc.head += head.children

        head_only_elements = [*get_head_only_elements(doc.body)]
        doc.head += head_only_elements

        with doc.head:
            # Add mandatory tags
            meta(charset="UTF-8")
            meta(name="viewport", content="width=device-width, initial-scale=1")

        # Add the better shiny script at the end of the body, to improve initial page load time
        with doc.body:
            script(src="/static/better-shiny.js", type="module")

        return super().render(doc.render())


def get_head_only_elements(root: RenderResult) -> Iterator[dominate.tags.dom_tag]:
    # Iterate over every element in the body and the children of the body
    for element in root:
        # And find the elements that are head only elements
        # "title", "meta", "link", "base",
        if type(element) in (dominate.tags.title, dominate.tags.meta, dominate.tags.link, dominate.tags.base):
            yield element
            # Then remove them from the content of the body
            root.remove(element)
        # If the element has children, we recursively call this function
        elif isinstance(element, dominate.tags.dom_tag) and len(element.children):
            yield from get_head_only_elements(element)
