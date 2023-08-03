from dominate.tags import html_tag

from better_shiny.themes._base_theme import theme_factory


def theme_pico() -> html_tag:
    return theme_factory("https://cdn.jsdelivr.net/npm/@picocss/pico@1/css/pico.min.css")
