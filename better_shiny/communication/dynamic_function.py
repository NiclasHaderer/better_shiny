from typing import Callable, Any

from dominate.tags import html_tag

from .._local_storage import local_storage
from ..reactive import Value

DynamicFunctionId = str


class DynamicFunction:
    def __init__(
        self,
        func: Callable[..., html_tag],
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
        self._on_mount: list[Callable[[], Any]] = []
        self._on_unmount: list[Callable[[], Any]] = []
        self._first_call = True

        # Local storage
        self._local_storage = local_storage()

    def __call__(self) -> html_tag:
        self._local_storage.active_dynamic_function_id = self._dynamic_function_id
        result = self._func(*self._args, **self._kwargs)
        if self._first_call:
            for fn in self._on_mount:
                fn()

        self._first_call = False
        return result

    def destroy(self) -> None:
        for fn in self._on_unmount:
            fn()
        # TODO call the destroy method of
        #  1. child dynamic functions
        #  2. reactive values -> removes all subscribers on the value_change event

    def on_mount(self, fn: Callable[[], Any]) -> None:
        self._on_mount.append(fn)

    def on_unmount(self, fn: Callable[[], Any]) -> None:
        self._on_unmount.append(fn)
