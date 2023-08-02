class LocalStorage:
    def __init__(self):
        from better_shiny.app import BetterShiny

        self.app: BetterShiny | None = None
        self.active_request: str | None = None


_local_storage: LocalStorage | None = None


def local_storage() -> LocalStorage:
    global _local_storage
    if not _local_storage:
        _local_storage = LocalStorage()
    return _local_storage
