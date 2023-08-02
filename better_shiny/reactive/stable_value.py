from __future__ import annotations

from typing import TypeVar

T = TypeVar("T")


class StableValue:
    """
    A stable value is a value that is not reactive. It can be used to store values that are not
    reactive, and can be used in reactive functions.
    The value of a stable value can be changed, but it will not trigger a re-render.
    Stable values are stable and have the same value for every re-render of the function.
    """

    def __init__(self, value: T):
        self._old_value: T | None = None
        self._value = value

    def __call__(self) -> T:
        return self._value

    @property
    def old_value(self) -> T | None:
        return self._old_value

    def set(self, value: T) -> None:
        self._old_value = self._value
        self._value = value

    def __repr__(self) -> str:
        return self._value.__repr__()
