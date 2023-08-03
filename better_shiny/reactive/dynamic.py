from typing import Callable, TypeVar, Dict

from dominate.dom_tag import attr
from dominate.tags import div

from .._local_storage import local_storage
from .._types import RenderResult, RenderFunction

T = TypeVar("T", bound=RenderFunction)

_function_call_counter: Dict[int, int] = {}


def dynamic(lazy: bool = False) -> Callable[[T], T]:
    def wrapper(fn: T) -> T:
        local = local_storage()
        fn_id = id(fn)
        _function_call_counter[fn_id] = 0

        def inner(*args, **kwargs) -> RenderResult:
            session = local.active_session()

            # Add the endpoint instance to the endpoint
            dynamic_function_id = f"{fn_id}_{_function_call_counter[fn_id]}"
            _function_call_counter[fn_id] += 1

            session.create_dynamic_function(dynamic_function_id, args, kwargs, fn)

            outlet = div(id=dynamic_function_id)
            with outlet:
                attr(style="display: contents;", data_server_rendered="true")
                if lazy:
                    attr(data_lazy="true")
                else:
                    session(dynamic_function_id)

            return outlet

        # Mark the function as dynamic, that way we can check if a function is decorated with @dynamic
        inner.is_dynamic_function = True
        return inner

    return wrapper
