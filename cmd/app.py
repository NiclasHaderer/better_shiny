import os
from threading import Timer

import dominate.util
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from dominate.tags import *

from better_shiny import reactive
from better_shiny.app import BetterShiny
from better_shiny.elements import matplot_element, pandas_element
from better_shiny.events.handler import on
from better_shiny.reactive import dynamic
from better_shiny.utils import RepeatTimer

app = BetterShiny()


@dynamic()
def timer(start=0):
    count = reactive.Value(start, "count")
    double_count = reactive.Value(start * 2, "double")

    @reactive.on_mount()
    def on_mount():
        t = RepeatTimer(1, lambda: count.set(count.value_non_reactive + 1))
        t.daemon = True
        t.start()
        return lambda: t.cancel()

    @reactive.on_update(count)
    def on_count_change(_):
        double_count.set(count.value_non_reactive * 2)

    return div(p("Count: ", count()), p("Double Count: ", double_count()))


@dynamic()
def counter():
    count = reactive.Value(0)

    with dominate.util.container() as container:
        with button("Increase"):
            on("click", handler=lambda event, _: count.set(count.value_non_reactive + 1))

        with button("Decrease"):
            on("click", handler=lambda event, _: count.set(count.value_non_reactive - 1))

        p("Count: ", count())

    return container


@dynamic(lazy=True)
def lazy_reactive_html():
    with dominate.util.container() as container:
        plot()
        timer(10)
        p("Hello World" * 10)

    return container


@dynamic()
def stable_value():
    stable = reactive.StableValue(0)
    dynamic_value = reactive.Value(0)

    @reactive.on_mount()
    def on_mount():
        stable.set(100_000)

        t = Timer(2, lambda: dynamic_value.set(2))
        t.daemon = True
        t.start()

    return div(
        p(
            "Stable value: (will not re-render function, even though it was changed) ",
            "\n",
            "The new value will only be displayed after the dynamic value has changed and triggered a re-render.",
            stable(),
        ),
        p("Dynamic value: (will re-render function, after it was changed): ", dynamic_value()),
    )


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
    return matplot_element(plt)


@dynamic()
def dataframe():
    parent_folder = os.path.dirname(os.path.dirname(__file__))
    dataframe_folder = os.path.join(parent_folder, "dataframes")
    dataframe_path = os.path.join(dataframe_folder, "cereal.csv")
    df = pd.read_csv(dataframe_path)
    return pandas_element(df.head(10))


@app.page("/")
def home():
    with dominate.util.container() as root:
        h1("Counter")
        counter()
        hr()
        h1("Timer lazy")
        lazy_reactive_html()
        hr()
        h1("Timer with 0")
        timer()
        hr()
        h1("Timer with 1")
        timer(1)
        hr()
        h1("Dataframe")
        dataframe()
        hr()
        stable_value()

    with head() as h:
        title("My Website")

    return h, root
