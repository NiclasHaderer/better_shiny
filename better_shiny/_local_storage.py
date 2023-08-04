from typing import TYPE_CHECKING

from .utils import create_logger

if TYPE_CHECKING:
    from .communication.session import Session
    from .communication.dynamic_function import DynamicFunction

logger = create_logger(__name__)


class LocalStorage:
    def __init__(self):
        from .app import BetterShiny

        self.app: BetterShiny | None = None
        self._active_session_id: str | None = None
        self._active_dynamic_function_id: str | None = None

    @property
    def active_session_id(self) -> str | None:
        return self._active_session_id

    @active_session_id.setter
    def active_session_id(self, value: str | None):
        self._active_session_id = value

    @property
    def active_dynamic_function_id(self) -> str | None:
        return self._active_dynamic_function_id

    @active_dynamic_function_id.setter
    def active_dynamic_function_id(self, value: str | None):
        self._active_dynamic_function_id = value

    def active_session(self) -> "Session":
        if self.active_session_id is None:
            raise RuntimeError("No active session.")

        return self.app.session_collector.get(self.active_session_id)

    def active_dynamic_function(self) -> "DynamicFunction":
        if self.active_dynamic_function_id is None:
            raise RuntimeError("No active dynamic function.")
        return self.active_session().get_dynamic_function(self.active_dynamic_function_id)


_local_storage: LocalStorage | None = None


def local_storage() -> LocalStorage:
    global _local_storage
    if not _local_storage:
        _local_storage = LocalStorage()
    return _local_storage
