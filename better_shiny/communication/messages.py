from typing import Literal, Union

from pydantic import BaseModel, RootModel


class RequestReRender(BaseModel):
    type: Literal["rerender@request"]
    id: str


class RequestEvent(BaseModel):
    type: Literal["event@request"]
    id: str
    event: str


BetterShinyRequestsType = Union[RequestReRender, RequestEvent]


class BetterShinyRequests(RootModel):
    root: BetterShinyRequestsType


class ResponseReRender(BaseModel):
    type: Literal["rerender@response"]
    id: str
    html: str


class ResponseError(BaseModel):
    type: Literal["error@response"]
    error: str


BetterShinyResponsesType = Union[ResponseReRender, ResponseError]


class BetterShinyResponses(RootModel):
    root: BetterShinyResponsesType
