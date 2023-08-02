import { ResponseError, ResponseReRender } from "./client";
import {innerHTML} from "diffhtml";

export const rerenderHandler = (data: ResponseReRender) => {
  const html = data.html;
  const id = data.id;

  const element = document.getElementById(id)!;
  innerHTML(
    element,
    html,
  )
};

export const errorResponseHandler = (data: ResponseError) => {
  console.error(data.error);
};
