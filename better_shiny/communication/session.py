import asyncio
from typing import Dict, Callable

from dominate.tags import html_tag
from starlette.websockets import WebSocket, WebSocketState

from .dynamic_function import DynamicFunctionId, DynamicFunction
from .._local_storage import local_storage
from ..reactive import Value

SessionId = str


class Session:
    def __init__(self, session_id: SessionId):
        self.session_id: SessionId = session_id
        self.websocket: WebSocket | None = None
        self._dynamic_functions: Dict[DynamicFunctionId, DynamicFunction] = {}
        self._local_storage = local_storage()

    @property
    def is_active(self) -> bool:
        return self.websocket is not None and self.websocket.client_state == WebSocketState.CONNECTED

    def destroy(self) -> None:
        for instance in self._dynamic_functions.values():
            instance.destroy()

    def get_dynamic_function(self, dynamic_function_id: DynamicFunctionId) -> DynamicFunction:
        if dynamic_function_id not in self._dynamic_functions:
            raise ValueError(f"Instance with id {dynamic_function_id} does not exist")

        return self._dynamic_functions[dynamic_function_id]

    def create_dynamic_function(
        self,
        dynamic_function_id: DynamicFunctionId,
        args: tuple,
        kwargs: dict,
        func: Callable[..., html_tag],
    ) -> None:
        if dynamic_function_id in self._dynamic_functions:
            raise ValueError(
                f"Dynamic function with id {dynamic_function_id} already exists in session {self.session_id}"
            )

        self._dynamic_functions[dynamic_function_id] = DynamicFunction(
            args=args, kwargs=kwargs, dynamic_function_id=dynamic_function_id, func=func
        )

    def rerender_on_change(self, dynamic_function_id: DynamicFunctionId, value: Value) -> None:
        app = self._local_storage.app

        def cb(_: Value) -> None:
            # noinspection PyProtectedMember
            asyncio.run(
                app._rerender_component(
                    session_id=self.session_id,
                    dynamic_function_id=dynamic_function_id,
                    websocket=self.websocket,
                )
            )

        value.on_update(cb)

    def __call__(self, dynamic_function_id: DynamicFunctionId) -> html_tag:
        self._local_storage.active_session_id = self.session_id
        result = self.get_dynamic_function(dynamic_function_id)()
        self._local_storage.active_session_id = None
        return result
