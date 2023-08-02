from typing import Callable

from .._local_storage import local_storage
from ..communication.session_collector import Session, EndpointInstance


def on_mount():
    """
    Decorator to register a function to be called when the function is mounted/called for the first time.
    """

    local = local_storage()

    def wrapper(fn: Callable[[], None]):
        def inner():
            fn()

        endpoint: EndpointInstance = local.active_dynamic_function()
        endpoint.on_mount(inner)

        return inner

    return wrapper


def on_unmount():
    """
    Decorator to register a function to be called when the function is unmounted/the connection to the client is
    interrupted
    """

    def wrapper(fn: Callable[[], None]):
        def inner():
            fn()

        return inner

    return wrapper
