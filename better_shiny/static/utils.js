export const retryEvery = async (cb, ms) => {
    let done = await cb()
    while (!done) {
        await sleep(ms)
        done = await cb()
    }
}

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));