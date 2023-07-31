from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict

from starlette.websockets import WebSocket

EndpointId = str


@dataclass
class EndpointInstance:
    args: tuple
    kwargs: dict
    endpoint: Endpoint

    def __call__(self):
        return self.endpoint.handler(*self.args, **self.kwargs)


class Endpoint:
    def __init__(self, handler_id: EndpointId, handler: Callable):
        self.handler_id: EndpointId = handler_id
        self.handler: Callable = handler
        self._instances: Dict[WebSocket, EndpointInstance] = {}

    def add_instance(self, websocket: WebSocket, args: tuple, kwargs: dict):
        self._instances[websocket] = EndpointInstance(
            args=args,
            kwargs=kwargs,
            endpoint=self,
        )

    def has_instance(self, websocket: WebSocket):
        return websocket in self._instances

    def call_instance(self, websocket: WebSocket):
        return self._instances[websocket]()


class EndpointCollector:

    def __init__(self):
        self._handlers: Dict[EndpointId, Endpoint] = {}

    def add(self, handler_id: EndpointId, handler: Callable):
        if handler_id in self._handlers:
            raise ValueError(f"Handler with id {handler_id} already exists")

        self._handlers[handler_id] = Endpoint(
            handler_id=handler_id,
            handler=handler,
        )

    def get(self, handler_id: str) -> Endpoint:
        if handler_id not in self._handlers:
            raise ValueError(f"Handler with id {handler_id} does not exist")

        return self._handlers[handler_id]

    def remove(self, handler_id: str):
        if handler_id not in self._handlers:
            raise ValueError(f"Handler with id {handler_id} does not exist")

        del self._handlers[handler_id]
