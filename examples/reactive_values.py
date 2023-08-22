from dominate.tags import *
from dominate.util import *

from better_shiny import reactive
from better_shiny.app import BetterShiny
from better_shiny.reactive import dynamic, on

app = BetterShiny()


@dynamic()
def counter():
    # Create a reactive value. Every time the value is changed, the UI will be updated.
    count = reactive.Value(0)

    # Create a container for all the other ui elements
    # Containers are not displayed. They are just a way to group elements together.
    with container() as c:
        # Create a button that will decrease the count by 1 when clicked
        with button("Decrease"):
            # Subscribe to the button's click event. If the button is clicked, the counter will be decreased by 1.
            # Make sure that you get the value using the get() function.
            on("click", handler=lambda event, _: count.set(count.get() - 1))

        # Create a button that will increase the count by 1 when clicked
        with button("Increase"):
            on("click", handler=lambda event, _: count.set(count.get() + 1))

        # Display the current count
        # You can access a reactive value by calling it like a function.
        # Only if you call it like a function, your ui will be updated when the value changes.
        p("Count: ", count())

    return c


@app.page('/')
def home():
    # Call the counter function to get the ui elements
    return counter()


app.run()
