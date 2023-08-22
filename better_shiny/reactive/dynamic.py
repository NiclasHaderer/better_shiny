import functools
import inspect
from typing import Callable, TypeVar, Dict

from dominate.dom_tag import attr
from dominate.tags import div

from .._local_storage import local_storage
from .._types import RenderResult, RenderFunction
from ..utils.logging import log_duration

T = TypeVar("T", bound=RenderFunction)

_function_call_counter: Dict[int, int] = {}


def dynamic(lazy: bool = False) -> Callable[[T], T]:
    def wrapper(fn: T) -> T:
        # Make sure that the function that is decorated with @dynamic is not a function inside a function
        def _assert_not_nested() -> None:
            if inspect.stack()[2].function != "<module>":
                raise RuntimeError(
                    "@dynamic can only be used on functions that are defined in the module scope. \n"
                    f"Move the function {fn.__name__} to the module scope. "
                )

        _assert_not_nested()

        local = local_storage()
        fn_id = id(fn)
        _function_call_counter[fn_id] = 0

        @functools.wraps(fn)
        def inner(*args, **kwargs) -> RenderResult:
            session = local.active_session()

            # Add the endpoint instance to the endpoint
            dynamic_function_id = f"{fn_id}_{_function_call_counter[fn_id]}"
            _function_call_counter[fn_id] += 1
            local.active_dynamic_function_id = dynamic_function_id

            session.create_dynamic_function(dynamic_function_id, args, kwargs, fn, fn.__name__)

            outlet = div(id=dynamic_function_id)
            with outlet:
                attr(style="display: contents;", data_server_rendered="true")
                if lazy:
                    attr(data_lazy="true")
                else:
                    log_duration(session.get_dynamic_function(dynamic_function_id), fn.__name__)()
            local.active_dynamic_function_id = None
            return outlet

        # Mark the function as dynamic, that way we can check if a function is decorated with @dynamic
        inner.is_dynamic_function = True
        return inner

    return wrapper
