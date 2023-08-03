from dominate.tags import html_tag

from better_shiny.themes._base_theme import theme_factory


def theme_pure() -> html_tag:
    return theme_factory("https://cdn.jsdelivr.net/npm/purecss@3.0.0/build/pure-min.css")
