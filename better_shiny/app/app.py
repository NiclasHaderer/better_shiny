import logging
import os

from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from starlette.websockets import WebSocketDisconnect
from websockets.exceptions import ConnectionClosedError

from better_shiny.communication import BetterShinyRequests, BetterShinyRequestsType, RequestReRender, ResponseError, \
    CommunicationHandler, ResponseReRender

logger = logging.getLogger(__name__)


class BetterShiny(FastAPI):

    thread_local_key = "better_shiny_api"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        static_dir = os.path.join(parent_dir, "static")
        self.mount("/static", StaticFiles(directory=static_dir), name="static")

        self.communication_handler = CommunicationHandler()
        self.add_api_websocket_route("/api/better-shiny-communication", self._register_communication_handler)

    async def _register_communication_handler(self, websocket: WebSocket):
        await websocket.accept()

        await websocket.send_json({
            "type": "hello@response",
        })

        while True:
            try:
                json_data = await websocket.receive_json()
                parsed_data: BetterShinyRequestsType = BetterShinyRequests(**json_data).root
            except (WebSocketDisconnect, ConnectionClosedError):
                break
            except Exception as e:
                logger.warning("Client error:", e)
                await websocket.send_json(
                    ResponseError(
                        type="error@response",
                        error=f"Error: {e}"
                    ).model_dump()
                )
                continue
            try:
                await self._delegate_to_communication_handler(parsed_data, websocket)
            except Exception as e:
                pass

    async def _delegate_to_communication_handler(self, parsed_data: BetterShinyRequestsType, websocket: WebSocket):
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
        html = self.communication_handler.get_handler(parsed_data.id)()
        await websocket.send_json(
            ResponseReRender(
                type="rerender@response",
                html=html
            ).model_dump()
        )
