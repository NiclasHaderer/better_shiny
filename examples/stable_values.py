from dominate.tags import *
from dominate.util import *

from better_shiny import reactive
from better_shiny.app import BetterShiny
from better_shiny.reactive import dynamic, on

app = BetterShiny()


@dynamic()
def some_component():
    value = reactive.Value(0)
    stable_value = reactive.StableValue(0)

    with container() as c:
        with button("Increase"):
            # As you can see, the value is updated every time the button is clicked.
            # This is because the value is reactive.
            on("click", handler=lambda event, _: value.set(value.value_non_reactive + 1))

        with button("Increase stable"):
            # The stable value will not trigger a UI update.
            # Only after the value is changed, and the changing of the value triggers a UI update, the change
            # in the stable value will also be reflected in the ui
            # in the stable value will also be reflected in the ui
            on("click", handler=lambda event, _: stable_value.set(stable_value() + 1))

        p("Value: ", value())
        p("Stable value: ", stable_value())

    return c


@app.page('/')
def home():
    with container() as c:
        title("My Website")
        some_component()

    return c


app.run()
