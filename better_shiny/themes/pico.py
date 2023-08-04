import dominate.util
from dominate.tags import html_tag, style
from dominate.util import raw

from better_shiny.themes._base_theme import theme_factory


def theme_pico() -> html_tag:
    with dominate.util.container() as container:
        theme_factory("https://cdn.jsdelivr.net/npm/@picocss/pico@1/css/pico.min.css")
        style(
            raw(
                """
                button {
                    width: unset;
                    display: inline-block;
                }
                """
            )
        )

    return container