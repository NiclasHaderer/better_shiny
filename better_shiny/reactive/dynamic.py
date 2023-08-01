from typing import Callable, TypeVar

from dominate.dom_tag import attr
from dominate.tags import div, html_tag

from .._local_storage import local_storage
from ..app import BetterShiny

T = TypeVar("T", bound=Callable[..., html_tag])


def dynamic(lazy: bool = False):
    def wrapper(fn: T) -> T:
        route_id = str(id(fn))
        local = local_storage()
        api = local.app
        endpoint = api.endpoint_collector.add(route_id, fn)

        if not api or not isinstance(api, BetterShiny):
            raise RuntimeError("No BetterShiny instance found in thread local storage. ")

        def inner(*args, **kwargs) -> html_tag:
            # Add the endpoint instance to the endpoint
            endpoint.add_instance(local.active_request, args, kwargs)

            outlet = div(id=route_id)
            with outlet:
                attr(style="display: contents;", data_server_rendered="true")
                if lazy:
                    attr(data_lazy="true")
                else:
                    fn(*args, **kwargs)

            return outlet

        return inner

    return wrapper
