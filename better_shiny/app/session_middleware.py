import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class UniqueSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        # Set the session cookie
        response.set_cookie("better_shiny_session", str(uuid.uuid4()), httponly=True)
        return response
