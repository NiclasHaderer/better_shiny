import {ResponseError, ResponseReRender} from "./client";
import {innerHTML} from "diffhtml";
import {populateLazyData} from "./lazy.ts";

export const rerenderHandler = (data: ResponseReRender) => {
    const html = data.html;
    const id = data.id;

    const element = document.getElementById(id);
    if (element) {
        innerHTML(element, html);
        void populateLazyData(element);
    }
};

export const errorResponseHandler = (data: ResponseError) => {
    console.error(data.error);
};
