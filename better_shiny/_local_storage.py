class LocalStorage:
    def __init__(self):
        from .app import BetterShiny

        self.app: BetterShiny | None = None
        self.active_session_id: str | None = None
        self.active_dynamic_function_id: str | None = None

    def get_endpoint(self):
        self.app.endpoint_collector.get(self.active_dynamic_function_id)

    def get_endpoint_instance(self):
        return self.app.endpoint_collector.get(
            self.active_dynamic_function_id
        ).get_instance(self.active_session_id)


_local_storage: LocalStorage | None = None


def local_storage() -> LocalStorage:
    global _local_storage
    if not _local_storage:
        _local_storage = LocalStorage()
    return _local_storage
