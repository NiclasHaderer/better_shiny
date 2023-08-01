import threading
from dataclasses import dataclass

from better_shiny.app import BetterShiny


@dataclass
class LocalStorage:
    app: BetterShiny | None
    active_request: str | None = None


_thread_local = threading.local()
_thread_local.value = LocalStorage(app=None, active_request=None)


def local_storage() -> LocalStorage:
    return _thread_local.value
