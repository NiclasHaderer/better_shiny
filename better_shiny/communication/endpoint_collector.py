from __future__ import annotations

import asyncio
import threading
import time
from dataclasses import dataclass
from typing import Callable, Dict, Any

from starlette.websockets import WebSocket, WebSocketState

from .._local_storage import local_storage
from ..reactive import Value

EndpointId = str
SessionId = str


@dataclass
class EndpointInstance:
    def __init__(
        self,
        args: tuple,
        kwargs: dict,
        endpoint: Endpoint,
        websocket: WebSocket | None,
        creation_time: float,
    ):
        self._args = args
        self._kwargs = kwargs
        self._endpoint = endpoint
        self.websocket = websocket
        self.creation_time = creation_time
        self._on_mount: list[Callable[[], Any]] = []
        self._on_unmount: list[Callable[[], Any]] = []
        self._first_call = True
        self._local_storage = local_storage()

    def __call__(self):
        upper_dyn_function = self._local_storage.active_dynamic_function_id
        self._local_storage.active_dynamic_function_id = (
            self._endpoint.dynamic_function_id
        )
        result = self._endpoint.func(*self._args, **self._kwargs)
        self._local_storage.active_dynamic_function_id = upper_dyn_function
        if self._first_call:
            for fn in self._on_mount:
                fn()

        self._first_call = False
        return result

    def remove(self):
        for fn in self._on_unmount:
            fn()

    def add_on_mount(self, fn: Callable[[], Any]):
        self._on_mount.append(fn)

    def add_on_unmount(self, fn: Callable[[], Any]):
        self._on_unmount.append(fn)

    @property
    def first_call(self):
        return self._first_call

    def is_alive(self):
        return (
            self.websocket is not None
            and self.websocket.client_state == WebSocketState.CONNECTED
            and
            # Has to be older than 10 seconds
            time.time() - self.creation_time > 10
        )


class Endpoint:
    def __init__(self, dynamic_function_id: EndpointId, handler: Callable):
        self.dynamic_function_id: EndpointId = dynamic_function_id
        self.func: Callable = handler
        self._instances: Dict[SessionId, EndpointInstance] = {}
        self._cleanup_manager()
        self._local_storage = local_storage()

    def _cleanup_manager(self):
        # Start a thread that runs the function self._cleanup every 10 seconds
        thread = threading.Thread(target=self._cleanup, args=())
        thread.daemon = True
        thread.start()

    def _cleanup(self):
        while True:
            time.sleep(30)
            for session_id in [*self._instances]:
                if not self._instances[session_id].is_alive():
                    self._instances[session_id].remove()
                    del self._instances[session_id]

    def remove(self):
        for instance in self._instances.values():
            instance.remove()

    def get_instance(self, session_id: str) -> EndpointInstance:
        if session_id not in self._instances:
            raise ValueError(f"Instance with id {session_id} does not exist")

        return self._instances[session_id]

    def add_instance(self, session_id: SessionId, args: tuple, kwargs: dict):
        self._instances[session_id] = EndpointInstance(
            args=args,
            kwargs=kwargs,
            endpoint=self,
            websocket=None,
            creation_time=time.time(),
        )

    def rerender_on_change(
        self, session_id: SessionId, dynamic_function_id: str, value: Value
    ):
        app = self._local_storage.app

        # noinspection PyProtectedMember
        def cb(_: Value):
            if session_id not in self._instances:
                subscription.unsubscribe()
                return

            instance = self._instances[session_id]
            if not instance.is_alive():
                subscription.unsubscribe()
                return

            # Run async function sync
            asyncio.run(
                app._rerender_component(
                    session_id, dynamic_function_id, instance.websocket
                )
            )

        subscription = value.on_update(cb)

    def add_ws_to_instance(self, websocket: WebSocket, session_id: SessionId):
        self._instances[session_id].websocket = websocket

    def has_instance(self, session_id: SessionId):
        return session_id in self._instances and self._instances[session_id].is_alive()

    def call_instance(self, session_id: SessionId) -> EndpointInstance:
        return self._instances[session_id]()


class EndpointCollector:
    def __init__(self):
        self._handlers: Dict[EndpointId, Endpoint] = {}

    def add(self, dynamic_function_id: EndpointId, handler: Callable) -> Endpoint:
        if dynamic_function_id in self._handlers:
            raise ValueError(f"Handler with id {dynamic_function_id} already exists")

        self._handlers[dynamic_function_id] = Endpoint(
            dynamic_function_id=dynamic_function_id,
            handler=handler,
        )
        return self._handlers[dynamic_function_id]

    def get(self, dynamic_function_id: str) -> Endpoint:
        if dynamic_function_id not in self._handlers:
            raise ValueError(f"Handler with id {dynamic_function_id} does not exist")

        return self._handlers[dynamic_function_id]

    def remove(self, dynamic_function_id: str):
        if dynamic_function_id not in self._handlers:
            raise ValueError(f"Handler with id {dynamic_function_id} does not exist")

        self._handlers[dynamic_function_id].remove()
        del self._handlers[dynamic_function_id]
