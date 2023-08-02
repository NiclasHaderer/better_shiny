import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from dominate.tags import *

from better_shiny import reactive
from better_shiny.app import BetterShiny
from better_shiny.elements import matplot_element, pandas_element
from better_shiny.reactive import dynamic
from better_shiny.utils import RepeatTimer

app = BetterShiny()


@dynamic()
def counter(start=0):
    count = reactive.Value(start, "count")
    double_count = reactive.Value(start * 2, "double")

    @reactive.on_mount()
    def on_mount():
        def increase():
            count.set(count.value_non_reactive + 1)

        timer = RepeatTimer(1, increase)
        timer.start()

    @reactive.on_update(count)
    def on_count_change(_):
        double_count.set(count.value_non_reactive * 2)

    return div(p("Count: ", count()), p("Double Count: ", double_count()))


@dynamic(lazy=True)
def lazy_reactive_html():
    return div("Lazy counter", counter(10))


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
    root = div(id="root")
    with root:
        with div():
            h1("Lazy Reactive")
            lazy_reactive_html()
            hr()
            h1("Counter with 0")
            counter()
            hr()
            h1("Counter with 1")
            counter(1)
            hr()
            h1("Plot")
            plot()
            hr()
            h1("Dataframe")
            dataframe()

    h = head()
    with h:
        title("My Website")

    return h, root
