import {createClient} from "./client.js";
import {errorResponseHandler, rerenderHandler} from "./message-handlers.js";

window.onload = async () => {
    const client = await createClient();
    client.onMessage(message => {
        switch (message.type) {
            case 'rerender@response':
                rerenderHandler(message)
                break;
            case 'error@response':
                errorResponseHandler(message)
                break;
        }
    })
    await populateInitialData();
}


const populateInitialData = async () => {
    const client = await createClient();
    const elementsToRenderOnTheServer = [...
        document.querySelectorAll("[data-server-rendered='true']")
    ]

    for (const element of elementsToRenderOnTheServer) {
        client.send({
            type: 'rerender@request',
            id: element.id,
        })
    }
}