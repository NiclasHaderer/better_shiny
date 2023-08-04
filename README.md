# Better Shiny: A Python Web Framework for Interactive Data Visualization

## What is Better Shiny?

Better Shiny is a Python web framework designed for interactive data visualization and creating dynamic web
applications. Inspired by the popular R Shiny framework, Better Shiny provides an easy-to-use and expressive way to
build web applications with minimal effort. It leverages Python's reactivity model to enable real-time updates to the
user interface based on user input or data changes.

## Getting Started

### Hello world

```python
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
```

### Reactive Values

```python
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
            # Make sure that you get the value using the value_non_reactive property.
            on("click", handler=lambda event, _: count.set(count.value_non_reactive - 1))

        # Create a button that will increase the count by 1 when clicked
        with button("Increase"):
            on("click", handler=lambda event, _: count.set(count.value_non_reactive + 1))

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
```

### Stable Values

```python
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
```

### Lifecycle Hooks

```python
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
```

### Subscribing to Values

```python
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
        _interval = set_interval(lambda: count.set(count.value_non_reactive + 1), 1)

        # Save the interval so that we can cancel it later
        interval.set(_interval)

    @reactive.on_unmount()
    def on_unmount():
        # Cancel the interval when the component is unmounted
        _interval = interval()
        if _interval is not None:
            _interval.cancel()

    @reactive.on_update(count)
    def on_count_change(_):
        # When the count changes, update the count_backwards value
        count_backwards.set(duration - count.value_non_reactive)

    # If the countdown is finished, cancel the interval
    if count_backwards.value_non_reactive <= 0:
        _interval = interval()
        if _interval is not None:
            _interval.cancel()

    if count_backwards.value_non_reactive <= 0:
        # This function will be called when the restart button is clicked
        def restart(event: Dict[str, Any], data: Any):
            count.set(0)
            interval.set(set_interval(lambda: count.set(count.value_non_reactive + 1), 1))

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
```

### Themes

```python
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
```

### Lazy Loading

```python
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
```

### Custom Components

```python
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from dominate.tags import *
from dominate.util import *

from better_shiny.app import BetterShiny
from better_shiny.elements import matplot_element, pandas_element
from better_shiny.reactive import dynamic

app = BetterShiny()


@dynamic(lazy=True)
def plot():
    # Generating random data for the scatter plot
    num_points = 50
    x = np.random.rand(num_points)
    y = np.random.rand(num_points)
    colors = np.random.rand(num_points)
    sizes = np.random.randint(10, 100, num_points)

    # Creating the scatter plot
    plt.scatter(x, y, c=colors, s=sizes, alpha=0.7, cmap="viridis")
    plt.colorbar()

    # Adding labels and title
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")
    plt.title("Random Scatter Plot")

    # Use the matplot_element to display a matplotlib plot
    return matplot_element(plt)


@dynamic(lazy=True)
def dataframe():
    parent_folder = os.path.dirname(os.path.dirname(__file__))
    dataframe_folder = os.path.join(parent_folder, "dataframes")
    dataframe_path = os.path.join(dataframe_folder, "cereal.csv")
    df = pd.read_csv(dataframe_path)
    # Use the pandas_element to display a dataframe
    # You could also use the table_element, or the dict_element to display tabular data
    return pandas_element(df.head(10))


@app.page('/')
def home():
    with container() as c:
        title("My Website")
        h1("Plot")
        plot()
        hr()
        h2("Dataframe")
        dataframe()
        hr()

    return c


app.run()
```