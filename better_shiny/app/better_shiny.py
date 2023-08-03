import functools
import os
import random
import uuid
from pathlib import Path
from typing import Callable

from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.types import Receive, Scope, Send
from starlette.websockets import WebSocketDisconnect
from websockets.exceptions import ConnectionClosedError

from .dominator_response import DominatorResponse
from .._local_storage import local_storage
from .._types import RenderFunction, RenderResult
from ..utils import create_logger
from ..communication import (
    BetterShinyRequests,
    BetterShinyRequestsType,
    RequestReRender,
    ResponseError,
    SessionCollector,
    ResponseReRender,
    RequestEvent,
)

logger = create_logger(__name__)


class BetterShiny:
    def __init__(self, *args, **kwargs):
        self.fast_api = FastAPI(*args, **kwargs)
        # Host static files
        static_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/static"
        self.serve_static_files(static_dir)

        # Add middlewares
        self.fast_api.add_middleware(SessionMiddleware, secret_key=random.randbytes(64))

        # Register session handler
        self.session_collector = SessionCollector()
        self.fast_api.add_api_websocket_route("/api/better-shiny-communication", self._ws_responder)
        self.fast_api.get("/api/better-shiny-communication/online")(self._online_check)

        self._local_storage = local_storage()
        if self._local_storage.app:
            raise RuntimeError("BetterShiny instance already exists in thread local storage. ")
        self._local_storage.app = self

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        await self.fast_api(scope, receive, send)

    def serve_static_files(self, folder_path: str | Path, route: str = "/static") -> None:
        self.fast_api.mount(route, StaticFiles(directory=folder_path))

    def page(self, path: str) -> Callable[[RenderFunction], Callable[..., DominatorResponse]]:
        def wrapper(fn: RenderFunction) -> Callable[..., DominatorResponse]:
            @functools.wraps(fn)
            def new_call(*args, **kwargs) -> DominatorResponse:
                session_id = str(uuid.uuid4())
                self.session_collector.add(session_id)
                local_storage().active_session_id = session_id
                logger.info(f"Request {session_id} started")
                html = fn(*args, **kwargs)
                logger.info(f"Request {session_id} ended")
                local_storage().active_session_id = None
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
            except Exception as e:
                # Client sent invalid data
                logger.warning("Client error:", e)
                await websocket.send_json(ResponseError(type="error@response", error=f"Error: {e}").model_dump())
                continue
            try:
                # Delegate the client request to the correct dynamic function
                await self._delegate_to_dynamic_function(parsed_data, websocket)
            except Exception as e:
                logger.error("Server error:")
                logger.exception(e)

    async def _delegate_to_dynamic_function(self, parsed_data: BetterShinyRequestsType, websocket: WebSocket) -> None:
        # switch between the different types of parsed_data
        match parsed_data:
            case RequestReRender():
                logger.info(f"Received request to re-render {parsed_data.id}")
                await self._handle_re_render_request(parsed_data, websocket)
            case RequestEvent():
                logger.info(f"Received request to handle event {parsed_data.id}")
                await self._handle_event_request(parsed_data, websocket)
            case _:
                logger.warning(f"Unknown request type: {parsed_data}")
                await websocket.send_json(
                    ResponseError(
                        type="error@response",
                        error=f"Unknown request type: {parsed_data}",
                    ).model_dump()
                )

    async def _handle_event_request(self, parsed_data: RequestEvent, websocket: WebSocket) -> None:
        session_id = websocket.headers.get("cookie", "").split("better_shiny_session_id=")[-1].split(";")[0]
        # Prepare and teardown the local storage for the dynamic function execution
        self._local_storage.active_session_id = session_id

        session = self._local_storage.active_session()
        dynamic_function = session.get_dynamic_function(parsed_data.id)
        dynamic_function.call_event(parsed_data.event_handler_id, parsed_data.event)

    async def _handle_re_render_request(self, parsed_data: RequestReRender, websocket: WebSocket) -> None:
        session_id = websocket.headers.get("cookie", "").split("better_shiny_session_id=")[-1].split(";")[0]
        await self._rerender_component(session_id, parsed_data.id, websocket)

    async def _rerender_component(self, session_id: str, dynamic_function_id: str, websocket: WebSocket) -> None:
        # Prepare and teardown the local storage for the dynamic function execution
        self._local_storage.active_session_id = session_id
        session = self._local_storage.active_session()
        html = session(dynamic_function_id=dynamic_function_id)
        self._local_storage.active_session_id = None

        assert isinstance(html, RenderResult)
        html = html.render()
        await websocket.send_json(
            ResponseReRender(type="rerender@response", html=html, id=dynamic_function_id).model_dump()
        )
