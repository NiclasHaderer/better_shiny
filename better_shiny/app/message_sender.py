import asyncio
from typing import Tuple, TYPE_CHECKING

from pydantic import BaseModel
from starlette.websockets import WebSocket, WebSocketDisconnect
from websockets.exceptions import ConnectionClosedError

from ..utils import create_logger

if TYPE_CHECKING:
    from .better_shiny import BetterShiny

logger = create_logger(__name__)


class MessageSender:
    def __init__(self, app: "BetterShiny"):
        self._messages_to_send: asyncio.Queue[Tuple[WebSocket, BaseModel]] = asyncio.Queue()
        self._register_message_sender()

    def _register_message_sender(self):
        event_loop = asyncio.get_event_loop()
        event_loop.create_task(self._message_sender())

    async def _message_sender(self):
        while True:
            websocket, message = await self._messages_to_send.get()
            try:
                dumped_message = message.model_dump()
                await websocket.send_json(dumped_message)
                logger.debug(f"Sent message to client")
            except (WebSocketDisconnect, ConnectionClosedError):
                pass
            except Exception as e:
                logger.error(e)
            finally:
                self._messages_to_send.task_done()

    def queue_message(self, websocket: WebSocket, message: BaseModel) -> None:
        self._messages_to_send.put_nowait((websocket, message))
