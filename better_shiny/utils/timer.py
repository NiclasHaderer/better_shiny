import asyncio
from typing import Callable


def set_timeout(func: Callable[[], None], timeout: float) -> asyncio.Task:
    from .._local_storage import local_storage

    local = local_storage()

    async def task_wrapper():
        await asyncio.sleep(timeout)
        func()

    loop = local.app.event_loop
    return loop.create_task(task_wrapper())


def set_interval(func: Callable[[], None], interval: float) -> asyncio.Task:
    from .._local_storage import local_storage

    local = local_storage()

    async def task_wrapper():
        while True:
            await asyncio.sleep(interval)
            func()

    loop = local.app.event_loop
    return loop.create_task(task_wrapper())
