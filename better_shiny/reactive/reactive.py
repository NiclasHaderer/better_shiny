from typing import Callable, TypeVar

from dominate.dom_tag import attr
from dominate.tags import div, html_tag

from .._local_storage import local_storage
from ..app import BetterShiny

T = TypeVar("T", bound=Callable[..., html_tag])


def _generate_answer(fun: Callable, args: tuple, kwargs: dict) -> Callable:
    def _answer():
        return div("No longer loading...")

    return _answer


def dynamic():
    # TODO: Give each decorated function a unique id and register it.
    def wrapper(fn: T) -> T:
        route_id = str(id(fn))
        api = local_storage().app
        if not api or not isinstance(api, BetterShiny):
            raise RuntimeError("No BetterShiny instance found in thread local storage. ")

        def inner(*args, **kwargs) -> html_tag:
            api.endpoint_collector.add(route_id, _generate_answer(fn, args, kwargs))

            outlet = div(id=route_id)
            with outlet:
                attr(style="display: contents;", data_server_rendered="true")

            return outlet

        return inner

    return wrapper
