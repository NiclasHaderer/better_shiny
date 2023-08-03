import asyncio
from typing import Callable

from .._local_storage import local_storage

local = local_storage()


def set_timeout(func: Callable[[], None], timeout: float) -> asyncio.Task:
    async def task_wrapper():
        await asyncio.sleep(timeout)
        func()
    loop = asyncio.get_event_loop()
    return loop.create_task(task_wrapper())


def set_interval(func: Callable[[], None], interval: float) -> asyncio.Task:
    async def task_wrapper():
        while True:
            await asyncio.sleep(interval)
            func()

    loop = asyncio.get_event_loop()
    return loop.create_task(task_wrapper())
