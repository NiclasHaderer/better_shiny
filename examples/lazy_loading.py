from dominate.tags import *
from dominate.util import *

from better_shiny.app import BetterShiny
from better_shiny.reactive import dynamic

app = BetterShiny()


# Just imagine that this component is very heavy to load (creates some plots, etc...)
# By making it lazy; it will be loaded after the rest of the page has already loaded, thereby 
# improving the perceived performance of the website.
@dynamic(lazy=True)
def lazy_component():
    return p("Lazy component")


@app.page('/')
def home():
    with container() as c:
        title("My Website")
        # The lazy component will only be loaded when the button is clicked
        lazy_component()

    return c


app.run()
