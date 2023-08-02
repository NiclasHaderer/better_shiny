export interface RequestReRender {
  type: "rerender@request";
  id: string;
}

export interface RequestEvent {
  type: "event@request";
  id: string;
  event: string;
}

export type BetterShinyRequests = RequestReRender | RequestEvent;

export interface ResponseReRender {
  type: "rerender@response";
  id: string;
  html: string;
}

export interface ResponseError {
  type: "error@response";
  error: string;
}

export type BetterShinyResponses = ResponseReRender | ResponseError;
