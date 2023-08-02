import { createClient } from "./client";
import { errorResponseHandler, rerenderHandler } from "./message-handlers";
import { retryEvery } from "./utils";

window.onload = async () => {
  const client = await createClient();
  client.onMessage(message => {
    switch (message.type) {
      case "rerender@response":
        rerenderHandler(message);
        break;
      case "error@response":
        errorResponseHandler(message);
        break;
    }
  });
  client.onClose(() => {
    retryEvery(async () => {
      return client.serverOnline().then(online => {
        if (online) window.location.reload();
        return online;
      });
    }, 300);
  });

  void populateLazyData();
};

const populateLazyData = async () => {
  const client = await createClient();
  const elementsToRenderOnTheServer = [...document.querySelectorAll("[data-server-rendered='true'][data-lazy='true']")];

  for (const element of elementsToRenderOnTheServer) {
    client.send({
      type: "rerender@request",
      id: element.id,
    });
  }
};
