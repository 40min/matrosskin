from uuid import uuid4


class SessionStorage:
    """ Simple storage for user's session ids"""

    _users_sessions: {str: str} = dict()

    def get(self, username: str) -> str:
        if username not in self._users_sessions:
            self._users_sessions[username] = str(uuid4())
        return self._users_sessions[username]

    def drop(self, username: str):
        if username in self._users_sessions:
            del self._users_sessions[username]


session_storage = SessionStorage()
