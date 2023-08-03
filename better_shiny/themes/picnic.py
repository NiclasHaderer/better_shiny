from dominate.tags import html_tag

from better_shiny.themes._base_theme import theme_factory


def theme_picnic() -> html_tag:
    return theme_factory("https://cdnjs.cloudflare.com/ajax/libs/picnic/7.1.0/picnic.min.css")
