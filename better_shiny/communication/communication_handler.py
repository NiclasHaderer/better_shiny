from dataclasses import dataclass
from typing import Callable, Dict


@dataclass
class _Handler:
    handler_id: str
    handler: Callable
    args: tuple
    kwargs: dict

    def __call__(self, *args, **kwargs):
        return self.handler(*args, *self.args, **kwargs, **self.kwargs)


class CommunicationHandler:

    def __init__(self):
        self._handlers: Dict[str, _Handler] = {}

    def register_new_handler(self, handler_id: str, handler: Callable, *args, **kwargs):
        if handler_id in self._handlers:
            raise ValueError(f"Handler with id {handler_id} already exists")

        self._handlers[handler_id] = _Handler(
            handler_id=handler_id,
            handler=handler,
            args=args,
            kwargs=kwargs,
        )

    def get_handler(self, handler_id: str) -> _Handler:
        if handler_id not in self._handlers:
            raise ValueError(f"Handler with id {handler_id} does not exist")

        return self._handlers[handler_id]

    def remove_handler(self, handler_id: str):
        if handler_id not in self._handlers:
            raise ValueError(f"Handler with id {handler_id} does not exist")

        del self._handlers[handler_id]
