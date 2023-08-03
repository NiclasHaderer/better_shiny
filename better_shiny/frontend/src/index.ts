import { createClient } from "./client";
import { errorResponseHandler, rerenderHandler } from "./message-handlers";
import { retryEvery } from "./utils";
import { populateLazyData } from "./lazy";

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

  void populateLazyData(document.body);
};
