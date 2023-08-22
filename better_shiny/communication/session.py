import time
from typing import Dict, List, Callable

from starlette.websockets import WebSocket, WebSocketState

from .dynamic_function import DynamicFunctionId, DynamicFunction
from .._local_storage import local_storage
from .._types import RenderFunction
from ..reactive import Value

SessionId = str


class Session:
    def __init__(self, session_id: SessionId):
        self.session_id: SessionId = session_id
        self.websocket: WebSocket | None = None
        self._dynamic_functions: Dict[DynamicFunctionId, DynamicFunction] = {}
        self._local_storage = local_storage()
        self._startup_time = time.time()
        self._delayed_executions: List[Callable[[], None]] = []

    @property
    def is_active(self) -> bool:
        """
        The session is active if the websocket is connected or the startup time is less than 60 seconds ago
        :return:
        """
        return (
            self.websocket is not None
            and self.websocket.client_state == WebSocketState.CONNECTED
            or (time.time() - self._startup_time < 60)
        )

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
        func: RenderFunction,
            name: str
    ) -> None:
        if dynamic_function_id in self._dynamic_functions:
            raise ValueError(
                f"Dynamic function with id {dynamic_function_id} already exists in session {self.session_id}"
            )

        self._dynamic_functions[dynamic_function_id] = DynamicFunction(
            args=args, kwargs=kwargs, dynamic_function_id=dynamic_function_id, func=func, name=name
        )

    def rerender_on_change(self, dynamic_function_id: DynamicFunctionId, value: Value) -> None:
        app = self._local_storage.app

        def invoke_rerender(inner_value: Value, skip_delayed_executions: bool = False) -> None:
            if not self.is_active:
                # Websocket has closed and the session will be cleaned up soon
                return

            if self.websocket is None:
                # No connection established (yet) -> waits for a websocket connection to be established
                self._delayed_executions.append(lambda: invoke_rerender(inner_value, skip_delayed_executions=True))
                return

            if len(self._delayed_executions) > 0 and not skip_delayed_executions:
                for delayed_execution in self._delayed_executions:
                    delayed_execution()
                self._delayed_executions.clear()

            # noinspection PyProtectedMember
            app._rerender_component(
                session_id=self.session_id,
                dynamic_function_id=dynamic_function_id,
                websocket=self.websocket,
            )

        dynamic_function = self.get_dynamic_function(dynamic_function_id)
        dynamic_function.listen_for_changes(value, invoke_rerender)
