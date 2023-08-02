from __future__ import annotations

from typing import Callable, TypeVar, Any, List, Generic

from .._local_storage import local_storage

T = TypeVar("T")


class ValueSubscription:
    def __init__(self, cb: Callable[[], Any]):
        self._cb = cb

    def unsubscribe(self) -> None:
        self._cb()


DestroyCb = Callable[[T], Any]


class Value(Generic[T]):
    # TODO bind a reactive value to a websocket connection, so if the websocket connection
    #  is closed, the value is destroyed and no re-renders are triggered
    # TODO: track where the value is used, and re-render on update.

    def __init__(self, value: T):
        self._value = value
        self._old_value: T | None = None
        self._on_update_callbacks: List[Callable[[Value[T]], Any]] = []
        self._on_destroy_callbacks: List[DestroyCb] = []
        self._local_storage = local_storage()

    @property
    def old_value_non_reactive(self) -> T | None:
        return self._old_value

    @property
    def value_non_reactive(self) -> T:
        return self._value

    def set(self, value: T) -> None:
        old_value = self._value
        self._value = value
        for cb in self._on_update_callbacks:
            for _on_destroy_callback in self._on_destroy_callbacks:
                _on_destroy_callback(old_value)
            self._on_destroy_callbacks.clear()

            destroy_cb = cb(self)
            if destroy_cb:
                self._on_destroy_callbacks.append(destroy_cb)

    def on_update(self, cb: Callable[[Value[T]], DestroyCb | None]) -> ValueSubscription:
        """
        This function is called when the value is updated
        """
        self._on_update_callbacks.append(cb)
        return ValueSubscription(lambda: self._on_update_callbacks.remove(cb))

    def __call__(self) -> T:
        session = self._local_storage.active_session()
        session.rerender_on_change(self._local_storage.active_dynamic_function_id, self)
        return self._value

    def destroy(self) -> None:
        for cb in self._on_destroy_callbacks:
            cb(self._value)
        self._on_destroy_callbacks = []
        self._on_update_callbacks = []

    def __repr__(self) -> str:
        return self._value.__repr__()


def on_update(
    value: Value[T],
) -> Callable[[Callable[[Value[T]], DestroyCb]], Callable[[Value[T]], DestroyCb]]:
    def wrapper(fn: Callable[[Value[T]], DestroyCb]) -> Callable[[Value[T]], DestroyCb]:
        def inner(_: Value[T]) -> DestroyCb:
            return fn(value)

        value.on_update(inner)

        return inner

    return wrapper
