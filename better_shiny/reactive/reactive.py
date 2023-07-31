from typing import Callable, TypeVar

from dominate.dom_tag import attr
from dominate.tags import div, html_tag

from .._local_storage import local_storage
from ..app import BetterShiny

T = TypeVar("T", bound=Callable[..., html_tag])


def _route_wrapper(fun: Callable) -> Callable:
    def _answer(args: tuple, kwargs: dict):
        return div("No longer loading...")

    return _answer


def dynamic():
    # TODO: Give each decorated function a unique id and register it.
    def wrapper(fn: T) -> T:
        route_id = str(id(fn))
        local = local_storage()
        api = local.app

        if not api or not isinstance(api, BetterShiny):
            raise RuntimeError("No BetterShiny instance found in thread local storage. ")

        def inner_function_executor_0_0_(*args, **kwargs) -> html_tag:
            # TODO Get the current session id and save the endpoint with the associated id

            outlet = div(id=route_id)
            with outlet:
                attr(style="display: contents;", data_server_rendered="true")
                fn(*args, **kwargs)

            return outlet

        api.endpoint_collector.add(route_id, _route_wrapper(fn))

        return inner_function_executor_0_0_

    return wrapper
