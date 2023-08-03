from threading import Timer
from typing import Callable


class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


def set_timeout(func: Callable[[], None], timeout: float) -> Timer:
    timer = Timer(timeout, func)
    timer.daemon = True
    timer.start()
    return timer


def set_interval(func: Callable[[], None], interval: float) -> RepeatTimer:
    timer = RepeatTimer(interval, func)
    timer.daemon = True
    timer.start()
    return timer
