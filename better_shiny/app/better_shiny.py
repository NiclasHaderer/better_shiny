import asyncio
import functools
import os
import random
import threading
import uuid
from asyncio import AbstractEventLoop
from pathlib import Path
from typing import Callable, Any, Coroutine

from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError
from starlette.middleware.sessions import SessionMiddleware
from starlette.types import Receive, Scope, Send
from starlette.websockets import WebSocketDisconnect
from websockets.exceptions import ConnectionClosedError

from .dominator_response import DominatorResponse
from .message_sender import MessageSender
from .._local_storage import local_storage
from .._types import RenderFunction, RenderResult
from ..communication import (
    BetterShinyRequests,
    BetterShinyRequestsType,
    RequestReRender,
    ResponseError,
    SessionCollector,
    ResponseReRender,
    RequestEvent,
)
from ..utils import create_logger

logger = create_logger(__name__)


class BetterShiny:
    def __init__(self, *args, **kwargs):
        self.fast_api = FastAPI(*args, **kwargs)
        self.event_loop: AbstractEventLoop | None = None
        self.event_loop_thread = None
        # Host static files
        static_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/static"
        self.serve_static_files(static_dir)

        # Add middlewares
        self.fast_api.add_middleware(SessionMiddleware, secret_key=random.randbytes(64))
        self.fast_api.on_event("startup")(self._set_event_loop)
        # Register session handler
        self.session_collector = SessionCollector()
        self.fast_api.add_api_websocket_route("/api/better-shiny-communication", self._ws_responder)
        self.fast_api.get("/api/better-shiny-communication/online")(self._online_check)

        self._local_storage = local_storage()
        if self._local_storage.app:
            raise RuntimeError("BetterShiny instance already exists in thread local storage. ")
        self._local_storage.app = self
        self._message_sender = MessageSender(self)

    def run(self, *args, **kwargs):
        import uvicorn

        uvicorn.run(self, *args, **kwargs)

    async def _set_event_loop(self) -> None:
        self.event_loop = asyncio.get_running_loop()
        self.event_loop_thread = threading.current_thread()
        self._message_sender.start(self.event_loop)
        self.session_collector.start()

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        await self.fast_api(scope, receive, send)

    def serve_static_files(self, folder_path: str | Path, route: str = "/static") -> None:
        self.fast_api.mount(route, StaticFiles(directory=folder_path))

    def page(
            self, path: str
    ) -> Callable[
        [Callable[[Any], Any]], Callable[[tuple[Any, ...], dict[str, Any]], Coroutine[Any, Any, DominatorResponse]]
    ]:
        def wrapper(
                fn: RenderFunction,
        ) -> Callable[[tuple[Any, ...], dict[str, Any]], Coroutine[Any, Any, DominatorResponse]]:
            @functools.wraps(fn)
            async def new_call(*args, **kwargs) -> DominatorResponse:
                session_id = str(uuid.uuid4())
                self.session_collector.add(session_id)
                self._local_storage.active_session_id = session_id
                logger.info(f"Request {session_id} started")
                html = fn(*args, **kwargs)
                logger.info(f"Request {session_id} ended")
                self._local_storage.active_session_id = None
                response = DominatorResponse(html)
                response.set_cookie(
                    "better_shiny_session_id",
                    session_id,
                    httponly=True,
                    samesite="strict",
                )
                return response

            return self.fast_api.get(path, response_class=DominatorResponse)(new_call)

        return wrapper

    @staticmethod
    def _online_check() -> bool:
        return True

    async def _ws_responder(self, websocket: WebSocket) -> None:
        # get session cooke better_shiny_session
        session_id = websocket.headers.get("cookie", "").split("better_shiny_session_id=")[-1].split(";")[0]
        if not session_id:
            await websocket.close(code=1003, reason="No session cookie found.")
            return

        try:
            session = self.session_collector.get(session_id)
        except ValueError:
            await websocket.close(code=1003, reason="Session not found.")
            return

        await websocket.accept()
        session.websocket = websocket

        while True:
            try:
                # Get the data from the client
                json_data = await websocket.receive_json()
                parsed_data: BetterShinyRequestsType = BetterShinyRequests(**json_data).root
            except (WebSocketDisconnect, ConnectionClosedError):
                # Connection closed, so we can stop the loop
                self.session_collector.remove(session_id)
                break
            # Pydantic exception
            except ValidationError as e:
                # Client sent invalid data
                self._message_sender.queue_message(websocket, ResponseError(type="error@response", error=f"Error: {e}"))
                continue
            try:
                # Delegate the client request to the correct dynamic function
                self._delegate_to_dynamic_function(parsed_data, websocket)
            except Exception as e:
                logger.error("Server error:")
                logger.exception(e)

    def _delegate_to_dynamic_function(self, parsed_data: BetterShinyRequestsType, websocket: WebSocket) -> None:
        # switch between the different types of parsed_data
        match parsed_data:
            case RequestReRender():
                logger.info(f"Received request to re-render {parsed_data.id}")
                self._handle_re_render_request(parsed_data, websocket)
            case RequestEvent():
                logger.info(f"Received request to handle event {parsed_data.id}")
                self._handle_event_request(parsed_data, websocket)
            case _:
                logger.warning(f"Unknown request type: {parsed_data}")
                self._message_sender.queue_message(
                    websocket,
                    ResponseError(
                        type="error@response",
                        error=f"Unknown request type: {parsed_data}",
                    ),
                )

    def _handle_event_request(self, parsed_data: RequestEvent, websocket: WebSocket) -> None:
        session_id = websocket.headers.get("cookie", "").split("better_shiny_session_id=")[-1].split(";")[0]
        # Prepare and teardown the local storage for the dynamic function execution
        self._local_storage.active_session_id = session_id
        self._local_storage.active_dynamic_function_id = parsed_data.id
        session = self._local_storage.active_session()
        dynamic_function = session.get_dynamic_function(parsed_data.id)
        dynamic_function.call_event(parsed_data.event_handler_id, parsed_data.event)
        self._local_storage.active_dynamic_function_id = None
        self._local_storage.active_session_id = None

    def _handle_re_render_request(self, parsed_data: RequestReRender, websocket: WebSocket) -> None:
        session_id = websocket.headers.get("cookie", "").split("better_shiny_session_id=")[-1].split(";")[0]
        self._rerender_component(session_id, parsed_data.id, websocket)

    def _rerender_component(self, session_id: str, dynamic_function_id: str, websocket: WebSocket) -> None:
        # Prepare and teardown the local storage for the dynamic function execution
        self._local_storage.active_session_id = session_id
        self._local_storage.active_dynamic_function_id = dynamic_function_id
        dynamic_function = self._local_storage.active_dynamic_function()
        html = dynamic_function()
        self._local_storage.active_dynamic_function_id = None
        self._local_storage.active_session_id = None

        assert isinstance(html, RenderResult)
        html = html.render()
        self._message_sender.queue_message(
            websocket, ResponseReRender(type="rerender@response", html=html, id=dynamic_function_id)
        )
