import typing

import dominate.tags
from fastapi.encoders import ENCODERS_BY_TYPE
from starlette.responses import HTMLResponse

# find all classes inside dominate.tags, which extend the html_tag class
dominate_tags = [dominate.document]
for name, obj in dominate.tags.__dict__.items():
    if isinstance(obj, type) and issubclass(obj, dominate.tags.html_tag):
        dominate_tags.append(obj)

for tag in dominate_tags:
    ENCODERS_BY_TYPE[tag] = lambda x: x


class DominatorResponse(HTMLResponse):

    def render(self,
               content: dominate.tags.html_tag | typing.Tuple[dominate.tags.head, dominate.tags.html_tag]) -> bytes:
        """
        Render the content of the response.
        :param content: Two different types are supported:
            1. A dominate.tags.html_tag object, which is the root of the html document (if the html element is not a
            document, it will be wrapped in a document object).
            2. A tuple of two dominate.tags.html_tag objects, where the first is the head and the second is the body.
        :return:
        """

        # If the content is a tuple, the first element is the head and the second is the body
        if isinstance(content, tuple) or isinstance(content, list) and len(content) == 2:
            head = content[0]
            content = content[1]
        elif isinstance(content, dominate.tags.html_tag):
            # If the content is a "html_tag", we do not have a head
            head = None
        else:
            raise TypeError(f"App handler returned {type(content)} instead of html_tag or tuple.")

        # If the content is not a document, we wrap it in a document
        if not isinstance(content, dominate.document):
            doc = dominate.document(title="")
            doc.body += content
        else:
            doc = content

        # If we have a custom head, replace the default head of the dominate html document
        if head is not None:
            doc.head.clear()
            doc.head += head.children

        with doc.head:
            # Add mandatory tags
            dominate.tags.meta(charset='UTF-8')
            dominate.tags.meta(name='viewport', content='width=device-width, initial-scale=1')
            dominate.tags.script(src='/static/index.js', type="module")

        return super().render(doc.render())
