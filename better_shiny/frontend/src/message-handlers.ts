import { ResponseError, ResponseReRender } from "./client";

export const rerenderHandler = (data: ResponseReRender) => {
  const html = data.html;
  const id = data.id;

  const element = document.getElementById(id)!;
  element.innerHTML = html;
};

export const errorResponseHandler = (data: ResponseError) => {
  console.error(data.error);
};
