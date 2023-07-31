import threading
from dataclasses import dataclass

from better_shiny.app import BetterShiny


@dataclass
class LocalStorage:
    app: BetterShiny | None


_thread_local = threading.local()
_thread_local.value = LocalStorage(app=None)


def local_storage() -> LocalStorage:
    return _thread_local.value
