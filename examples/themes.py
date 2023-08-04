from dominate.tags import *
from dominate.util import *

from better_shiny.app import BetterShiny
from better_shiny.themes import theme_picnic

app = BetterShiny()


@app.page('/')
def home():
    with container() as c:
        # Include one of the themes
        theme_picnic()
        # theme_milligram()
        # theme_pico()
        # theme_chota()
        # theme_water()
        button("Button")
        input_(placeholder="Something")

    return c


app.run()
