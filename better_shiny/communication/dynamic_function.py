from typing import Callable, Any, Dict, Set, List


from .._local_storage import local_storage
from .._types import RenderFunction, RenderResult
from ..reactive import Value

DynamicFunctionId = str
LineNr = int


class DynamicFunction:
    def __init__(
        self,
        func: RenderFunction,
        dynamic_function_id: DynamicFunctionId,
        args: tuple,
        kwargs: dict,
    ):
        # Function arguments
        self._args = args
        self._kwargs = kwargs
        self._func = func
        self._dynamic_function_id = dynamic_function_id

        # Lifecycle hooks
        self._on_mount: List[Callable[[], Callable[[], Any] | None]] = []
        self._on_unmount: List[Callable[[], Any]] = []
        self._first_call = True

        # Stable values
        self._values: Dict[LineNr, Value] = {}
        self._values_to_listen_for_changes: Set[Value] = set()

        # Local storage
        self._local_storage = local_storage()

    def __call__(self) -> RenderResult:
        self._local_storage.active_dynamic_function_id = self._dynamic_function_id
        result = self._func(*self._args, **self._kwargs)
        if self._first_call:
            for fn in self._on_mount:
                on_destroy = fn()
                if on_destroy is not None:
                    self._on_unmount.append(on_destroy)

        self._first_call = False
        return result

    @property
    def is_first_call(self) -> bool:
        return self._first_call

    def destroy(self) -> None:
        for fn in self._on_unmount:
            fn()

        for value in self._values.values():
            value.destroy()
        # TODO call the destroy method of
        #  1. child dynamic functions

    def on_mount(self, fn: Callable[[], Callable[[], Any] | None]) -> None:
        self._on_mount.append(fn)

    def on_unmount(self, fn: Callable[[], Any]) -> None:
        self._on_unmount.append(fn)

    def add_value(self, call_line, value: Value) -> None:
        self._values[call_line] = value

    def has_value(self, call_line) -> bool:
        return call_line in self._values

    def get_value(self, call_line) -> Value:
        return self._values[call_line]

    def listen_for_changes(self, value: Value, invoke_rerender: Callable[[Value], None]) -> None:
        if value in self._values_to_listen_for_changes:
            return

        value.on_update(invoke_rerender)
        self._values_to_listen_for_changes.add(value)
