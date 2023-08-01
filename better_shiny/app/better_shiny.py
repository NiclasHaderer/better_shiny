import functools
import os
import random
import uuid
from pathlib import Path
from typing import Callable

from dominate.tags import html_tag
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.types import Receive, Scope, Send
from starlette.websockets import WebSocketDisconnect
from websockets.exceptions import ConnectionClosedError

from better_shiny._local_storage import local_storage
from better_shiny._utils import create_logger
from better_shiny.app.dominator_response import DominatorResponse
from better_shiny.communication import BetterShinyRequests, BetterShinyRequestsType, RequestReRender, ResponseError, \
    EndpointCollector, ResponseReRender

logger = create_logger(__name__)


class BetterShiny:
    def __init__(self, *args, **kwargs):
        self.fast_api = FastAPI(*args, **kwargs)
        # Host static files
        static_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/static"
        self.serve_static_files(static_dir)

        # Add middlewares
        self.fast_api.add_middleware(SessionMiddleware, secret_key=random.randbytes(64))

        # Register endpoint handler
        self.endpoint_collector = EndpointCollector()
        self.fast_api.add_api_websocket_route("/api/better-shiny-communication", self._register_endpoints)
        self.fast_api.get("/api/better-shiny-communication/online")(self._online_check)

        local_data = local_storage()
        if local_data.app:
            raise RuntimeError("BetterShiny instance already exists in thread local storage. ")
        local_data.app = self

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        await self.fast_api(scope, receive, send)

    def serve_static_files(self, folder_path: str | Path, route: str = "/static"):
        self.fast_api.mount(route, StaticFiles(directory=folder_path))

    def page(self, path: str):
        def wrapper(fn: Callable[..., html_tag]):
            @functools.wraps(fn)
            def new_call(*args, **kwargs):
                session_id = str(uuid.uuid4())
                local_storage().active_request = session_id
                logger.info(f"Request {session_id} started")
                html = fn(*args, **kwargs)
                logger.info(f"Request {session_id} ended")
                local_storage().active_request = None
                response = DominatorResponse(html)
                response.set_cookie("better_shiny_session_id", session_id, httponly=True, samesite="strict")
                return response

            return self.fast_api.get(path, response_class=DominatorResponse)(new_call)

        return wrapper

    @staticmethod
    def _online_check():
        return True

    async def _register_endpoints(self, websocket: WebSocket):
        # get session cooke better_shiny_session
        session_cookie = websocket.headers.get("cookie", "").split("better_shiny_session=")[-1].split(";")[0]
        if not session_cookie:
            await websocket.close(code=1003, reason="No session cookie found.")
            return

        await websocket.accept()

        while True:
            try:
                # Get the data from the client
                json_data = await websocket.receive_json()
                parsed_data: BetterShinyRequestsType = BetterShinyRequests(**json_data).root
            except (WebSocketDisconnect, ConnectionClosedError):
                # Connection closed, so we can stop the loop
                break
            except Exception as e:
                # Client sent invalid data
                logger.warning("Client error:", e)
                await websocket.send_json(
                    ResponseError(
                        type="error@response",
                        error=f"Error: {e}"
                    ).model_dump()
                )
                continue
            try:
                # Delegate the client request to the correct endpoint
                await self._delegate_to_endpoint(parsed_data, websocket)
            except Exception as e:
                logger.error("Server error:")
                logger.exception(e)

    async def _delegate_to_endpoint(self, parsed_data: BetterShinyRequestsType, websocket: WebSocket):
        # switch between the different types of parsed_data
        match parsed_data:
            case RequestReRender():
                logger.info(f"Received request to re-render {parsed_data.id}")
                await self._handle_re_render_request(parsed_data, websocket)
            case _:
                logger.warning(f"Unknown request type: {parsed_data}")
                await websocket.send_json(
                    ResponseError(
                        type="error@response",
                        error=f"Unknown request type: {parsed_data}"
                    ).model_dump()
                )

    async def _handle_re_render_request(self, parsed_data: RequestReRender, websocket: WebSocket):
        endpoint = self.endpoint_collector.get(parsed_data.id)
        session_id = websocket.headers.get("cookie", "").split("better_shiny_session_id=")[-1].split(";")[0]
        html = endpoint.call_instance(session_id)
        assert isinstance(html, html_tag)
        html = html.render()
        await websocket.send_json(
            ResponseReRender(
                type="rerender@response",
                html=html,
                id=parsed_data.id
            ).model_dump()
        )
