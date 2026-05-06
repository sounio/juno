"""Session Manager - Unified multi-device sessions."""

from typing import Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel
import uuid


class SessionContext(BaseModel):
    current_agent: str = "conversation"
    active_device: str = ""
    last_message_ts: str = ""
    metadata: dict[str, Any] = {}


class Session(BaseModel):
    id: str = ""
    user_id: str = ""
    title: str = "New Session"
    active_devices: list[str] = []
    context: SessionContext = SessionContext()
    created_at: str = ""
    updated_at: str = ""


class SessionManager:
    def __init__(self):
        self._sessions: dict[str, Session] = {}

    def create(self, user_id: str, device_id: str = "") -> Session:
        session = Session(
            id=str(uuid.uuid4()),
            user_id=user_id,
            active_devices=[device_id] if device_id else [],
            context=SessionContext(
                active_device=device_id,
                last_message_ts=datetime.now(timezone.utc).isoformat(),
            ),
            created_at=datetime.now(timezone.utc).isoformat(),
            updated_at=datetime.now(timezone.utc).isoformat(),
        )
        self._sessions[session.id] = session
        return session

    def get(self, session_id: str) -> Optional[Session]:
        return self._sessions.get(session_id)

    def get_user_sessions(self, user_id: str) -> list[Session]:
        return [s for s in self._sessions.values() if s.user_id == user_id]

    def get_active_session(self, user_id: str) -> Optional[Session]:
        sessions = self.get_user_sessions(user_id)
        return sessions[-1] if sessions else None

    def update_device_focus(self, session_id: str, device_id: str):
        session = self._sessions.get(session_id)
        if session:
            if device_id not in session.active_devices:
                session.active_devices.append(device_id)
            session.context.active_device = device_id
            session.updated_at = datetime.now(timezone.utc).isoformat()

    def join_device(self, session_id: str, device_id: str):
        session = self._sessions.get(session_id)
        if session and device_id not in session.active_devices:
            session.active_devices.append(device_id)
            session.updated_at = datetime.now(timezone.utc).isoformat()

    def remove_device(self, session_id: str, device_id: str):
        session = self._sessions.get(session_id)
        if session and device_id in session.active_devices:
            session.active_devices.remove(device_id)
            session.updated_at = datetime.now(timezone.utc).isoformat()


session_manager = SessionManager()
