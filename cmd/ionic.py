import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from dominate import document
from dominate.tags import *
from dominate.util import container, text, raw

from better_shiny import reactive
from better_shiny.app import BetterShiny
from better_shiny.elements import matplot_element, pandas_element
from better_shiny.reactive import dynamic, on
from better_shiny.themes import theme_picnic, theme_milligram, theme_pico, theme_chota, theme_water
from better_shiny.themes.ionic import *
from better_shiny.utils import set_timeout, set_interval

def ionic():
    with document() as root:
        attr(dir="ltr", lang="en")
        title("Ionic")
        theme_ionic()
        # ion_header
        with ion_header():
            with ion_toolbar(color="primary"):
                ion_title("Impressive Demo")

        # ion_content
        with ion_content():
            # ion_card
            with ion_card():
                img(src="https://picsum.photos/536/354", alt="Card Image", width="100%" , height="400px" , style="object-fit: cover;")
                # ion_card_header
                with ion_card_header():
                    ion_card_title("Welcome to the Demo!")
                # ion_card_content
                with ion_card_content():
                    p("This is a demo site built with Ionic.")
                    p("Feel free to explore and learn more about Ionic.")

            with ion_card():
                with ion_card_header():
                    ion_card_title("Buttons")

                with ion_card_content():
                    with ion_item():
                        ion_button("Default")
                        ion_button("Clear", fill="clear")
                        ion_button("Outline", fill="outline")
                        ion_button("Solid", fill="solid")

                    with ion_item():
                        ion_checkbox("I agree to the terms and conditions")
                    with ion_item():
                        ion_toggle("Enable Notifications", enableOnOffLabels=True)

                    with ion_item():
                        ion_chip("Default")
                        ion_chip("Disabled", disabled=True)
                        ion_chip("Outline", outline=True)
                    with ion_item():
                        ion_datetime("Date of birth")

            # ion_list
            with ion_list():
                # ion_item - Like
                with ion_item():
                    ion_icon(name="heart")
                    ion_label("Like")
                # ion_item - Share
                with ion_item():
                    ion_icon(name="share")
                    ion_label("Share")
                # ion_item - Rate
                with ion_item():
                    ion_icon(name="star")
                    ion_label("Rate")

            # ion_button
            with ion_button(expand="full", color="secondary", routerLink="/about"):
                text("Learn More")

    return root
