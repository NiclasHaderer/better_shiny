import { createClient } from "./client";
import { stringifyEvent } from "./stringify.ts";

export const reRegisterEvents = async (element: HTMLElement) => {
  const client = await createClient();

  const elementsToRegister = element.querySelectorAll("[data-listen-on-event='true']");
  for (const element of elementsToRegister) {
    const handler = element.getAttribute("data-listen-on-event-handler");
    const event = element.getAttribute(`data-${handler}`);
    if (!event || !handler) continue;

    (element as any)[`on${event}`] = (event: Event) =>
      client.send({
        type: "event@request",
        event: JSON.parse(stringifyEvent(event)),
        event_handler_id: handler,
        id: element.getAttribute("data-dynamic-function-id")!,
      });
  }
};
