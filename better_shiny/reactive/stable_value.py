from __future__ import annotations

import inspect
from typing import TypeVar, Generic

from .._local_storage import local_storage

T = TypeVar("T")


class _ValueMeta(type):
    def __call__(cls, *args, **kwargs):
        # Get the line of code where the value was created at.
        back = inspect.currentframe().f_back

        # Check if the function one back has a property called "is_reactive", for now Values can only be used in
        # reactive functions
        calling_function = back.f_globals[back.f_code.co_name]
        if not hasattr(calling_function, "is_dynamic_function"):
            raise ValueError("StableValue can only be used in a reactive function")

        call_line = back.f_lineno

        dynamic_function = local_storage().active_dynamic_function()
        if not dynamic_function.has_stable_value(call_line):
            instance = super(_ValueMeta, cls).__call__(*args, **kwargs)
            dynamic_function.add_stable_value(call_line, instance)

        return dynamic_function.get_stable_value(call_line)


class StableValue(Generic[T], metaclass=_ValueMeta):
    """
    A stable value is a value that is not reactive. It can be used to store values that are not
    reactive, and can be used in reactive functions.
    The value of a stable value can be changed, but it will not trigger a re-render.
    Stable values are stable and have the same value for every re-render of the function.
    """

    def __init__(self, value: T, name: str = ""):
        self._old_value: T | None = None
        self._value = value
        self._name = name

    def __call__(self) -> T:
        return self._value

    @property
    def old_value(self) -> T | None:
        return self._old_value

    def set(self, value: T) -> None:
        self._old_value = self._value
        self._value = value

    def __repr__(self) -> str:
        return f"{self._name}: {self._value.__repr__()}"
