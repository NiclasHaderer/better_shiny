import { ResponseError, ResponseReRender } from "./client";
import { populateLazyData } from "./lazy.ts";
import { reRegisterEvents } from "./events.ts";

export const rerenderHandler = (data: ResponseReRender) => {
  const html = data.html;
  const id = data.id;
  const startTime = Date.now()
  const element = document.getElementById(id);
  if (element) {
    element.innerHTML = html;
    void populateLazyData(element);
    void reRegisterEvents(element);
  }
    console.log(`Rerendered ${id} in ${Date.now() - startTime}ms`);
};

export const errorResponseHandler = (data: ResponseError) => {
  console.error(data.error);
};
