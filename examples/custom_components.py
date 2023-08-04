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
