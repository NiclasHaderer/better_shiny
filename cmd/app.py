from dominate.tags import *

from better_shiny import reactive
from better_shiny.app import BetterShiny
from better_shiny.reactive import dynamic

app = BetterShiny()


@dynamic()
def reactive_html(default_val: str, some_other: int):
    value = reactive.Value(default_val)

    return div(
        h2(value(), some_other),

    )


@app.page("/")
def home():
    root = div(id="root")
    with root:
        with div(id='header').add(ol()):
            for i in ['home', 'about', 'contact']:
                li(a(i.title(), href=f'/{i}.html'))

        with div():
            p('Lorem ipsum..')
            reactive_html("Hello", 1)

    h = head()
    with h:
        title('My Website')

    return h, root
