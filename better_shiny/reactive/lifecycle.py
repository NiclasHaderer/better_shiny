from typing import Callable


def on_mount():
    """
    Decorator to register a function to be called when the function is mounted/called for the first time.
    """

    def wrapper(fn: Callable[[], None]):
        def inner():
            fn()

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
