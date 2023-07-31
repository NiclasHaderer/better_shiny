import uuid

import dominate
from dominate.tags import *
from starlette.responses import Response

from better_shiny import reactive
from better_shiny.app import BetterShiny
from better_shiny.reactive import dynamic

app = BetterShiny()


@dynamic()
def reactive_html(default_val: str, some_other: int):
    value = reactive.Value(default_val)

    return div(
        h1(value()),
    )


@app.page("/")
def read_root(response: Response):
    uuid_value = uuid.uuid4()
    response.set_cookie("better_shiny_session", str(uuid_value), httponly=True)
    doc = dominate.document(title='Dominate your HTML')
    doc.head += meta(charset='UTF-8')
    doc.head += meta(name='viewport', content='width=device-width, initial-scale=1')
    doc.head += script(src='/static/index.js', type="module")

    with doc:
        with div(id='header').add(ol()):
            for i in ['home', 'about', 'contact']:
                li(a(i.title(), href=f'/{i}.html'))

        with div():
            p('Lorem ipsum..')
            reactive_html("Hello", 1)

    return doc.render()
