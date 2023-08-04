from dominate.dom_tag import attr
from dominate.tags import script, link
from dominate.util import container


def theme_ionic():
    with container() as c:
        with link():
            attr(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/@ionic/core@7/css/ionic.bundle.css")

        with script():
            attr(src="https://cdn.jsdelivr.net/npm/@ionic/core@7/dist/ionic/ionic.js", nomodule="")

        with script():
            attr(src="https://cdn.jsdelivr.net/npm/@ionic/core@7/dist/ionic/ionic.esm.js", type="module")

    return c
