from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .communication.session import Session
    from .communication.dynamic_function import DynamicFunction


class LocalStorage:
    def __init__(self):
        from .app import BetterShiny

        self.app: BetterShiny | None = None
        self.active_session_id: str | None = None
        self.active_dynamic_function_id: str | None = None

    def active_session(self) -> "Session":
        if not self.active_session_id:
            raise RuntimeError("No active session.")

        return self.app.session_collector.get(self.active_session_id)

    def active_dynamic_function(self) -> "DynamicFunction":
        if not self.active_dynamic_function_id:
            raise RuntimeError("No active dynamic function.")
        return self.active_session().get_dynamic_function(self.active_dynamic_function_id)


_local_storage: LocalStorage | None = None


def local_storage() -> LocalStorage:
    global _local_storage
    if not _local_storage:
        _local_storage = LocalStorage()
    return _local_storage
