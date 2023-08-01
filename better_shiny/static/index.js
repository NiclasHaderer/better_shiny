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
    client.onClose(() => {
        console.log('Connection closed. Refresh to reconnect.')
        setInterval(async () => {
            const online = await client.serverOnline()
            if (online) {
                window.location.reload()
            }
        }, 300)
    })
}


const populateLazyData = async () => {
    const client = await createClient();
    const elementsToRenderOnTheServer = [...
        document.querySelectorAll("[data-server-rendered='true'][data-lazy='true']")
    ]

    for (const element of elementsToRenderOnTheServer) {
        client.send({
            type: 'rerender@request',
            id: element.id,
        })
    }
}