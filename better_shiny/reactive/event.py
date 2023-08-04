from typing import TypeVar, Callable, Dict, Any

import dominate.dom_tag

from better_shiny._local_storage import local_storage

T = TypeVar("T")


def on(
    event: str,
    handler: Callable[[T, Dict[str, Any]], None],
    data: T | None = None,
) -> dominate.dom_tag.attr:
    event_handler_id = f"{event}-{id(handler)}"

    function = local_storage().active_dynamic_function()
    function.register_event_handler(event_handler_id, handler, data)

    attrs = {
        "data_listen_on_event": "true",
        "data_listen_on_event_handler": event_handler_id,
        "data_dynamic_function_id": local_storage().active_dynamic_function_id,
        f"data_{event_handler_id}": event,
    }

    return dominate.dom_tag.attr(**attrs)
