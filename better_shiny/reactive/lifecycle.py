from typing import Callable

from .._local_storage import local_storage


def on_mount() -> Callable[[Callable[[], None]], Callable[[], None]]:
    """
    Decorator to register a function to be called when the function is mounted/called for the first time.
    """

    local = local_storage()

    def wrapper(fn: Callable[[], None]) -> Callable[[], None]:
        def inner() -> None:
            return fn()

        dynamic_function = local.active_dynamic_function()
        if dynamic_function.is_first_call:
            dynamic_function.on_mount(inner)

        return inner

    return wrapper


def on_unmount() -> Callable[[Callable[[], None]], Callable[[], None]]:
    """
    Decorator to register a function to be called when the function is unmounted/the connection to the client is
    interrupted
    """

    def wrapper(fn: Callable[[], None]) -> Callable[[], None]:
        def inner() -> None:
            fn()

        dynamic_function = local_storage().active_dynamic_function()
        if dynamic_function.is_first_call:
            dynamic_function.on_unmount(inner)

        return inner

    return wrapper
