from typing import Callable, TypeVar, Dict

from dominate.dom_tag import attr
from dominate.tags import div, html_tag

from .._local_storage import local_storage

T = TypeVar("T", bound=Callable[..., html_tag])


def dynamic(lazy: bool = False):
    # Here to avoid circular imports
    from ..app import BetterShiny

    def wrapper(fn: T) -> T:
        function_id = str(id(fn))
        local = local_storage()
        api = local.app
        endpoint = api.endpoint_collector.add(function_id, fn)

        if not api or not isinstance(api, BetterShiny):
            raise RuntimeError("No BetterShiny instance found in thread local storage. ")

        def inner(*args, **kwargs) -> html_tag:
            # Add the endpoint instance to the endpoint
            endpoint.create_dynamic_function(local.active_session_id, args, kwargs)

            outlet = div(id=function_id)
            with outlet:
                attr(style="display: contents;", data_server_rendered="true")
                if lazy:
                    attr(data_lazy="true")
                else:
                    endpoint.call_instance(local.active_session_id)

            return outlet

        return inner

    return wrapper
