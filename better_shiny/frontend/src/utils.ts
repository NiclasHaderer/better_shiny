export const retryEvery = async (cb: () => boolean | Promise<boolean>, ms: number) => {
    let done = await cb()
    while (!done) {
        await sleep(ms)
        done = await cb()
    }
}

const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));