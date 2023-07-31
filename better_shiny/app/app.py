import logging
import os

from dominate.tags import html_tag
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from starlette.websockets import WebSocketDisconnect
from websockets.exceptions import ConnectionClosedError

from better_shiny.communication import BetterShinyRequests, BetterShinyRequestsType, RequestReRender, ResponseError, \
    EndpointCollector, ResponseReRender

logger = logging.getLogger(__name__)


class BetterShiny(FastAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Host static files
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        static_dir = os.path.join(parent_dir, "static")
        self.mount("/static", StaticFiles(directory=static_dir), name="static")

        # Register endpoint handler
        self.endpoint_collector = EndpointCollector()
        self.add_api_websocket_route("/api/better-shiny-communication", self._register_endpoints)

        from better_shiny._local_storage import local_storage
        local_data = local_storage()
        if local_data.app:
            raise RuntimeError("BetterShiny instance already exists in thread local storage. ")
        local_data.app = self

    async def _register_endpoints(self, websocket: WebSocket):
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
                logger.error("Server error:", e)

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
        # TODO
        # html = self.endpoint_collector.get(parsed_data.id)
        html = html_tag("Hello world", websocket.session)
        assert isinstance(html, html_tag)
        html = html.render()
        await websocket.send_json(
            ResponseReRender(
                type="rerender@response",
                html=html,
                id=parsed_data.id
            ).model_dump()
        )
