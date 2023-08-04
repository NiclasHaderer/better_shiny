from dominate.tags import *

from better_shiny.app import BetterShiny

app = BetterShiny()


@app.page('/')
def home():
    with p("Hello world") as paragraph:
        # Set the title of the page
        title("My Website")

    return paragraph


app.run()
