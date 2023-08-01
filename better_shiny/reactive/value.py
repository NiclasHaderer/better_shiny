from __future__ import annotations

from typing import Callable, TypeVar, Any, List

T = TypeVar("T")


class ValueSubscription:
    def __init__(self, cb: Callable[[], Any]):
        self._cb = cb

    def unsubscribe(self):
        self._cb()


DestroyCb = Callable[[T], Any]


class Value:
    # TODO bind a reactive value to a websocket connection, so if the websocket connection
    #  is closed, the value is destroyed and no re-renders are triggered
    # TODO: track where the value is used, and re-render on update.

    def __init__(self, value: T):
        self._value = value
        self._on_update_callbacks: List[Callable[[T, T], Any]] = []
        self._on_destroy_callbacks: List[DestroyCb] = []

    def on_update(self, cb: Callable[[T, T], DestroyCb]) -> ValueSubscription:
        """
        This function is called when the value is updated
        """
        self._on_update_callbacks.append(cb)
        return ValueSubscription(lambda: self._on_update_callbacks.remove(cb))

    def __call__(self) -> T:
        return self._value

    def set(self, value: T) -> None:
        old_value = self._value
        self._value = value
        for cb in self._on_update_callbacks:
            for _on_destroy_callback in self._on_destroy_callbacks:
                _on_destroy_callback(old_value)
            self._on_destroy_callbacks.append(cb(old_value, value))

    def __repr__(self):
        return self._value.__repr__()
