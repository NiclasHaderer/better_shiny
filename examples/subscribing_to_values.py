from asyncio import Task
from typing import Dict, Any

from dominate.tags import *
from dominate.util import *

from better_shiny import reactive
from better_shiny.app import BetterShiny
from better_shiny.reactive import dynamic, on
from better_shiny.utils import set_interval

app = BetterShiny()


# Please bear in mind that the following demonstration is not the best way to implement a countdown!
@dynamic()
def countdown(duration=0):
    count = reactive.Value(0)
    count_backwards = reactive.Value(duration)
    interval = reactive.StableValue[Task](None)

    @reactive.on_mount()
    def on_mount():
        # Start an interval that will increase the count by 1 every second
        task = set_interval(lambda: count.set(count.get() + 1), 1)

        # Save the interval so that we can cancel it later
        interval.set(task)

    @reactive.on_unmount()
    def on_unmount():
        # Cancel the interval when the component is unmounted
        task = interval.get()
        if task is not None:
            task.cancel()

    @reactive.on_update(count)
    def on_count_change(_):
        # When the count changes, update the count_backwards value
        count_backwards.set(duration - count.get())

    # If the countdown is finished, cancel the interval
    if count_backwards.get() <= 0:
        _interval = interval.get()
        if _interval is not None:
            _interval.cancel()

    if count_backwards.get() <= 0:
        # This function will be called when the restart button is clicked
        def restart(event: Dict[str, Any], data: Any):
            print(event, data)
            count.set(0)
            interval.set(set_interval(lambda: count.set(count.get() + 1), 1))

        with p("Countdown finished") as paragraph:
            with button("Restart"):
                # When the restart button is clicked, call the restart function
                # As you can see, you can pass data to the handler function. This is useful when iterating over a list
                # of items, and you want to know which item was clicked.
                on("click", handler=restart, data=None)

        return paragraph
    else:
        return div(
            # Display the current count
            p("Time elapsed: ", count()),
            # Display the time left
            p("Time left: ", count_backwards())
        )


@app.page('/')
def home():
    with container() as c:
        title("My Website")
        countdown(10)

    return c


app.run()
