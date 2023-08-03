from __future__ import annotations

import inspect
from typing import Callable, TypeVar, Any, List, Generic

from .._local_storage import local_storage

T = TypeVar("T")


class ValueSubscription:
    def __init__(self, cb: Callable[[], Any]):
        self._cb = cb

    def unsubscribe(self) -> None:
        self._cb()


class _ValueMeta(type):
    def __call__(cls, *args, **kwargs):
        # Get the line of code where the value was created at.
        back = inspect.currentframe().f_back

        # Check if the function one back has a property called "is_reactive", for now Values can only be used in
        # reactive functions
        calling_function = back.f_globals[back.f_code.co_name]
        if not hasattr(calling_function, "is_dynamic_function"):
            raise ValueError("Value can only be used in a reactive function")

        call_line = back.f_lineno

        dynamic_function = local_storage().active_dynamic_function()
        if not dynamic_function.has_value(call_line):
            instance = super(_ValueMeta, cls).__call__(*args, **kwargs)
            dynamic_function.add_value(call_line, instance)

        return dynamic_function.get_value(call_line)


class Value(Generic[T], metaclass=_ValueMeta):
    """
    def __new__(cls, *args, **kwargs):
        # Get the line of code where the value was created at.
        # This is used to track whether the value is used in a reactive function, and if so, allows me to return the
        # original value instead of a new instance, making this value stable.
        back = inspect.currentframe().f_back

        # Check if the function one back has a property called "is_reactive", for now Values can only be used in
        # reactive functions
        calling_function = back.f_globals[back.f_code.co_name]
        if not hasattr(calling_function, "is_dynamic_function"):
            raise ValueError("Value can only be used in a reactive function")

        call_line = back.f_lineno

        dynamic_function = local_storage().active_dynamic_function()
        if not dynamic_function.has_value(call_line):
            self = super().__new__(cls)
            dynamic_function.add_value(call_line, self)

        return dynamic_function.get_value(call_line)
    """

    def __init__(self, value: T, name: str = ""):
        self._value = value
        self._old_value: T | None = None
        self._on_update_callbacks: List[Callable[[Value[T]], Any]] = []
        self._on_destroy_callbacks: List[DestroyCb] = []
        self._local_storage = local_storage()
        self._name = name

    @property
    def old_value_non_reactive(self) -> T | None:
        return self._old_value

    @property
    def value_non_reactive(self) -> T:
        return self._value

    def set(self, value: T) -> None:
        if self._value == value:
            return

        self._old_value = self._value
        self._value = value

        # Cleanup old callbacks
        for _on_destroy_callback in self._on_destroy_callbacks:
            _on_destroy_callback(self)

        self._on_destroy_callbacks.clear()

        # Call update callbacks
        for cb in self._on_update_callbacks:
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
            cb(self)
        self._on_destroy_callbacks = []
        self._on_update_callbacks = []

    def __repr__(self) -> str:
        return f"{self._name}: {self._value.__repr__()}"


def on_update(
    value: Value[T],
) -> Callable[[Callable[[Value[T]], DestroyCb]], Callable[[Value[T]], DestroyCb]]:
    def wrapper(fn: Callable[[Value[T]], DestroyCb]) -> Callable[[Value[T]], DestroyCb]:
        def inner(_: Value[T]) -> DestroyCb:
            return fn(value)

        dynamic_function = local_storage().active_dynamic_function()
        if dynamic_function.is_first_call:
            value.on_update(inner)

        return inner

    return wrapper


DestroyCb = Callable[[Value[T]], Any]
