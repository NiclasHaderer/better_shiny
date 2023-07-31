from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Callable, Dict

from starlette.websockets import WebSocket, WebSocketState

EndpointId = str
SessionId = str


@dataclass
class EndpointInstance:
    args: tuple
    kwargs: dict
    endpoint: Endpoint
    websocket: WebSocket | None
    creation_time: float

    def __call__(self):
        return self.endpoint.handler(*self.args, **self.kwargs)


class Endpoint:
    def __init__(self, handler_id: EndpointId, handler: Callable):
        self.handler_id: EndpointId = handler_id
        self.handler: Callable = handler
        self._instances: Dict[SessionId, EndpointInstance] = {}
        self._cleanup_manager()

    def _cleanup_manager(self):
        # Start a thread that runs the function self._cleanup every 10 seconds
        thread = threading.Thread(target=self._cleanup, args=())
        thread.daemon = True
        thread.start()

    def _cleanup(self):
        while True:
            time.sleep(10)
            for session_id in self._instances:
                if (
                        self._instances[session_id].websocket is not None and
                        self._instances[session_id].websocket.client_state == WebSocketState.DISCONNECTED
                ):
                    del self._instances[session_id]

    def add_instance(self, session_id: SessionId, args: tuple, kwargs: dict):
        self._instances[session_id] = EndpointInstance(
            args=args,
            kwargs=kwargs,
            endpoint=self,
            websocket=None,
            creation_time=time.time(),
        )

    def add_ws_to_instance(self, websocket: WebSocket, session_id: SessionId):
        self._instances[session_id].websocket = websocket

    def has_instance(self, session_id: SessionId):
        return (
                session_id in self._instances and
                self._instances[session_id].websocket is not None and not
                self._instances[session_id].websocket.client_state == WebSocketState.DISCONNECTED
        )

    def call_instance(self, session_id: SessionId) -> EndpointInstance:
        return self._instances[session_id]()


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
