import { createClient } from "./client";

export const populateLazyData = async (rootElement: HTMLElement) => {
  const client = await createClient();
  const elementsToRenderOnTheServer = [
    ...rootElement.querySelectorAll("[data-server-rendered='true'][data-lazy='true']"),
  ];
  for (const element of elementsToRenderOnTheServer) {
    client.send({
      type: "rerender@request",
      id: element.id,
    });
  }
};
