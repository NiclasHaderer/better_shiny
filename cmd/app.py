import threading
import time

import matplotlib.pyplot as plt
import numpy as np
from dominate.tags import *

from better_shiny import reactive
from better_shiny.app import BetterShiny
from better_shiny.elements import matplot
from better_shiny.reactive import dynamic

app = BetterShiny()


@dynamic()
def counter(start=0):
    count = reactive.Value(start)

    @reactive.on_mount()
    def on_mount():
        stop_counting = False

        def increment():
            while not stop_counting:
                time.sleep(1)
                count.set(count() + 1)

        thread = threading.Thread(target=increment, daemon=True)
        thread.start()

        def tear_down():
            nonlocal stop_counting
            stop_counting = True
            thread.join()

        return tear_down

    return div(
        "Count: ", count(),
    )


@dynamic(lazy=True)
def lazy_reactive_html():
    return div(
        h2("Lazy"),
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
    plt.scatter(x, y, c=colors, s=sizes, alpha=0.7, cmap='viridis')
    plt.colorbar()

    # Adding labels and title
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.title('Random Scatter Plot')
    #
    return matplot(plt)


@app.page("/")
def home():
    root = div(id="root")
    with root:
        with div():
            lazy_reactive_html()
            counter()
            counter(1)
            plot()

    h = head()
    with h:
        title('My Website')

    return h, root
