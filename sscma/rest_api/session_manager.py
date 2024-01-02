from threading import Lock

from .pipeline import Pipeline
from .utils import SessionConfig


class SessionManager:
    def __init__(self, max_sessions: int = 32):
        self.sessions_lock = Lock()
        self.sessions = {}
        self.max_sessions = max_sessions

    def get_sessions_limit(self):
        return self.max_sessions

    def create_session(self, session_id: str, session_config: SessionConfig):
        with self.sessions_lock:
            if len(self.sessions) >= self.max_sessions:
                raise ResourceWarning(
                    f"Max sessions exceeded the limit of {self.max_sessions}"
                )
            new_session = Pipeline(session_config)
            self.sessions[session_id] = new_session

    def get_session(self, session_id: str):
        with self.sessions_lock:
            if session_id in self.sessions:
                return self.sessions[session_id]
            raise ValueError(f"Session {session_id} not exist")

    def get_all_sessions_id(self):
        with self.sessions_lock:
            return [str(key) for key in self.sessions]

    def remove_session(self, session_id: str):
        with self.sessions_lock:
            if session_id in self.sessions:
                self.sessions.pop(session_id)
                return True
            return False

    def remove_all_sessions(self):
        with self.sessions_lock:
            self.sessions = {}
