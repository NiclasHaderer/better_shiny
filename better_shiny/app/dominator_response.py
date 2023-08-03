import typing

from dominate import document
from dominate.tags import meta, script, head as dominate_head
from starlette.responses import HTMLResponse

from better_shiny._types import RenderResult


class DominatorResponse(HTMLResponse):
    def render(self, content: RenderResult | typing.Tuple[dominate_head, RenderResult]) -> bytes:
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
            doc = document(title="")
            doc.body += content
        else:
            doc = content

        # If we have a custom head, replace the default head of the dominate html document
        if head is not None:
            doc.head.clear()
            doc.head += head.children

        with doc.head:
            # Add mandatory tags
            meta(charset="UTF-8")
            meta(name="viewport", content="width=device-width, initial-scale=1")
            script(src="/static/better-shiny.js", type="module")

        return super().render(doc.render())
