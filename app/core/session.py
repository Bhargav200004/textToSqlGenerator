from fastapi import HTTPException
import uuid
from datetime import datetime
from app.models.domain import QuerrySession
from app.models.response import QueryStatus


class SessionManager:
    def __init__(self):
        self._store: dict[str, QuerrySession] = {}


    def create(self, question: str) -> QuerrySession:
        session = QuerrySession(
            session_id=str(uuid.uuid4()),
            original_question=question,
            status = QueryStatus.NEED_CLARIFICATION,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self._store[session.session_id] = session
        return session

    
    def load(self, session_id: str) -> QuerrySession:
        session = self._store.get(session_id)
        
        if not session:
            raise HTTPException(status_code = 404, detail = f"Session {session_id} not found")
        return session


    def save(self, session: QuerrySession) -> None:
        session.updated_at = datetime.utcnow()
        self._store[session.session_id] = session


    def delete(self, session_id) -> None:
        self._store.pop(session_id,None)