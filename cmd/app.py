from dominate.tags import *

from better_shiny import reactive
from better_shiny.app import BetterShiny
from better_shiny.reactive import dynamic

app = BetterShiny()


@dynamic()
def reactive_html(default_val: str):
    @reactive.on_mount()
    def on_mount():
        print("Mounted")
        stable_value.set("changed-stable")

    @reactive.on_unmount()
    def on_unmount():
        print("Unmounted")

    value = reactive.Value(default_val)
    stable_value = reactive.StableValue("stable")

    @value.on_update
    def update(old_val: str, new_val: str):
        print(f"Value updated from {old_val} to {new_val}")
        return lambda: print(f"Value {new_val} destroyed")

    return div(
        h3(value()),
        p("A stable value that does not trigger a re-render: ", i(stable_value())),
    )


@dynamic(lazy=True)
def lazy_reactive_html():
    return div(
        h2("Lazy"),
    )


@app.page("/")
def home():
    root = div(id="root")
    with root:
        with div():
            reactive_html("This is the title of my website")
            lazy_reactive_html()

    h = head()
    with h:
        title('My Website')

    return h, root
