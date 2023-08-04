"""
Go to https://ionicframework.com/docs/components and run the following code in the console:

```JavaScript
components = $$(".navbar-sidebar__item a.menu__link")
  .filter(e => e.href.startsWith(`${location.origin}/docs/api/`))
	.filter(e => e.innerText.startsWith("ion-"))
	.map(e => e.innerText)


conponents = [...new Set(components)]

classes = components.map(e =>{
  className = e.replaceAll("-", "_")
	return `
class ${className}(html_tag):
    tagname = "${e}"`
}).join("\n\n")


complete = `from dominate.tags import html_tag

${classes}

`

navigator.clipboard.writeText(complete)
```
"""

from .tags import *
from .ionic import theme_ionic