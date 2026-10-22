from pydantic import BaseModel
from typing import Optional
from enum import Enum

class QueryStatus(str , Enum):
    SQL_READY = "sql_ready"
    NEED_CLARIFICATION = "needs_clarification"
    ERROR = "error"


class QueryResponse(BaseModel):
    session_id : str
    status : QueryStatus
    sql: Optional[str] = None
    explanation : Optional[str] = None
    tables_used: list[str] = []
    clarification_question: Optional[str] = None
    error_message: Optional[str] = None

