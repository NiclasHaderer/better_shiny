from dominate.tags import *
from dominate.util import *

from better_shiny import reactive
from better_shiny.app import BetterShiny
from better_shiny.reactive import dynamic

app = BetterShiny()


@dynamic()
def some_page():
    # This function will be called when the page is mounted/rendered for the first time.
    @reactive.on_mount()
    def on_mount():
        print("Mounted")

        # Use this callback to clean up resources that have to be cleaned up (timers, etc...)
        return lambda: print("Unmounted")

    # This function will be called when the page is unmounted.
    @reactive.on_unmount()
    def on_unmount():
        print("Unmounted")

    return p("Some page")


@app.page('/')
def home():
    with container() as c:
        title("My Website")
        some_page()

    return c


app.run()
