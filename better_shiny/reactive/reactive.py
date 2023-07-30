import threading
from typing import Callable, TypeVar

from dominate.dom_tag import attr
from dominate.tags import div, html_tag
from fastapi import Request

from ..app import BetterShiny

T = TypeVar("T", bound=Callable[..., html_tag])


def _generate_answer(fun: Callable, args: tuple, kwargs: dict) -> Callable:
    def _answer(request: Request):
        return "Hello World"

    return _answer


def dynamic():
    # TODO: Give each decorated function a unique id and register it.
    def wrapper(fn: T) -> T:
        def inner(*args, **kwargs) -> html_tag:
            # TODO: Then create a unique id for every instance of the function (tied to a websocket connection)
            api = threading.local()[BetterShiny.thread_local_key]
            if not api or not isinstance(api, BetterShiny):
                raise RuntimeError("No BetterShiny instance found in thread local storage. ")

            # Generate a random route_id
            route_id = str(id(fn))
            api.communication_handler.register_new_handler(route_id, fn, args, kwargs)

            outlet = div(id=route_id)
            with outlet:
                attr(style="display: contents;", data_server_rendered="true")

            return outlet

        return inner

    return wrapper
