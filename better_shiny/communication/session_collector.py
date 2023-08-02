from __future__ import annotations

from typing import Dict

from better_shiny.communication.session import SessionId, Session


class SessionCollector:
    def __init__(self):
        self._sessions: Dict[SessionId, Session] = {}

    def add(self, session_id: SessionId) -> Session:
        if session_id in self._sessions:
            raise ValueError(f"Session with id {session_id} already exists")

        self._sessions[session_id] = Session(
            session_id=session_id,
        )
        return self._sessions[session_id]

    def get(self, dynamic_function_id: str) -> Session:
        if dynamic_function_id not in self._sessions:
            raise ValueError(f"Handler with id {dynamic_function_id} does not exist")

        return self._sessions[dynamic_function_id]

    def remove(self, dynamic_function_id: str):
        if dynamic_function_id not in self._sessions:
            raise ValueError(f"Handler with id {dynamic_function_id} does not exist")

        self._sessions[dynamic_function_id].destroy()
        del self._sessions[dynamic_function_id]
