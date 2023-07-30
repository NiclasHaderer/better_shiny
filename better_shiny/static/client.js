let client;


export const createClient = async () => {
    if (client) {
        return client;
    }

    client = _createClient();
    return client;
}

const _createClient = async () => {
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const socket = new WebSocket(`${protocol}://${window.location.host}/api/better-shiny-communication`);
    let _client = {
        send: (message) => socket.send(JSON.stringify(message)),
        onMessage: (callback) => {
            const onMessageWrapper = (event) => {
                callback(JSON.parse(event.data));
            }

            socket.addEventListener('message', onMessageWrapper)
            return {
                unsubscribe: () => socket.removeEventListener('message', onMessageWrapper)
            }
        }
    }
    _client.onerror = e => console.error(e);
    _client.onmessage = m => console.log(m);
    await new Promise(resolve => socket.onopen = resolve);
    return _client;
}