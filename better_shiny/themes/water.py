from dominate.tags import html_tag

from better_shiny.themes import theme_factory


def theme_water() -> html_tag:
    return theme_factory("https://cdn.jsdelivr.net/npm/water.css@2/out/water.css")
