from dominate.tags import html_tag

from better_shiny.themes._base_theme import theme_factory


def theme_chota() -> html_tag:
    return theme_factory("https://unpkg.com/chota@0.9.2/dist/chota.min.css")
