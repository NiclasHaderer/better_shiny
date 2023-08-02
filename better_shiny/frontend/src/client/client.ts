import {BetterShinyRequests, BetterShinyResponses} from "./messages.ts";


export interface Subscription {
    unsubscribe: () => void;
}

export interface Client {
    send: (message: BetterShinyRequests) => void;
    onMessage: (callback: (data: BetterShinyResponses) => any) => Subscription;
    onClose: (callback: (event: CloseEvent) => void) => Subscription;
    onError: (callback: (event: Event) => void) => Subscription;
    serverOnline: () => Promise<boolean>;
}


let client: Promise<Client>;


export const createClient = async (): Promise<Client> => {
    if (client) {
        return client;
    }

    client = _createClient();
    return client;
}

const _createClient = async () => {
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const socket = new WebSocket(`${protocol}://${window.location.host}/api/better-shiny-communication`);
    let _client: Client = {
        send: (message) => socket.send(JSON.stringify(message)),
        onMessage: (callback) => {
            const onMessageWrapper = (event: MessageEvent) => {
                callback(JSON.parse(event.data));
            }

            socket.addEventListener('message', onMessageWrapper)
            return {
                unsubscribe: () => socket.removeEventListener('message', onMessageWrapper)
            }
        },
        onClose: (callback) => {
            const onCloseWrapper = (event: CloseEvent) => {
                callback(event);
            }

            socket.addEventListener('close', onCloseWrapper)
            return {
                unsubscribe: () => socket.removeEventListener('close', onCloseWrapper)
            }
        },
        onError: (callback) => {
            const onErrorWrapper = (event: Event) => {
                callback(event);
            }

            socket.addEventListener('error', onErrorWrapper)
            return {
                unsubscribe: () => socket.removeEventListener('error', onErrorWrapper)
            }
        },
        serverOnline: async () => {
            return fetch('/api/better-shiny-communication/online').then(() => true).catch(() => false)
        }
    }
    await new Promise(resolve => socket.onopen = resolve);
    return _client;
}