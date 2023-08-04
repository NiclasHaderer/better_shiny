from dominate.util import container

from better_shiny.themes._base_theme import theme_factory


def theme_milligram() -> container:
    with container() as c:
        theme_factory("https://fonts.googleapis.com/css?family=Roboto:300,300italic,700,700italic")
        theme_factory("https://cdnjs.cloudflare.com/ajax/libs/normalize/8.0.1/normalize.min.css")
        theme_factory("https://cdnjs.cloudflare.com/ajax/libs/milligram/1.4.1/milligram.min.css")

    return c
