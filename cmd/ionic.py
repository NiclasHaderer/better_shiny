from dominate import document
from dominate.tags import *
from dominate.util import text

from better_shiny.themes.ionic import *


def ionic():
    with document() as root:
        attr(dir="ltr", lang="en", mode="ios")
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
                img(src="https://picsum.photos/1500/200?blur=10", alt="Card Image", width="100%", height="400px",
                    style="object-fit: cover;")
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
                        ion_chip("Default")
                        ion_chip("Disabled", disabled=True)
                        ion_chip("Outline", outline=True)

                    with ion_item():
                        span("Icons:")
                        ion_icon(name="basketball-outline")
                        ion_icon(name="bicycle-outline")
                        ion_icon(name="boat-outline")
                        ion_icon(name="body-outline")
                        ion_icon(name="bonfire-outline")
                        ion_icon(name="book-outline")
                        ion_icon(name="bookmark-outline")
                        ion_icon(name="bookmarks-outline")



            with ion_card():
                with ion_card_header():
                    ion_card_title("Inputs")

                with ion_card_content():
                    # ion-item with ion-input (Default Input)
                    with ion_item():
                        ion_input(label="Default Input", placeholder="Enter text")

                    # ion-item with ion-select
                    with ion_item():
                        with ion_select(label="Select", placeholder="Make a Selection"):
                            ion_select_option("No Game Console", value="")
                            ion_select_option("NES", value="nes")
                            ion_select_option("Nintendo64", value="n64")
                            ion_select_option("PlayStation", value="ps")
                            ion_select_option("Sega Genesis", value="genesis")
                            ion_select_option("Sega Saturn", value="saturn")
                            ion_select_option("SNES", value="snes")

                    # ion-item with ion-toggle
                    with ion_item():
                        ion_toggle("Toggle")

                    # ion-item with ion-checkbox
                    with ion_item():
                        ion_checkbox("Checkbox")

                    # ion-item with ion-range
                    with ion_item():
                        with ion_range(label_placement="start"):
                            div("Range", slot="label")

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
