from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.response import QueryStatus

class ColumnMeta(BaseModel):
    name: str
    type: str
    nullable: bool
    description: str = ""
    primary_key: bool = False


class TableMeta(BaseModel):
    name: str
    columns: list[ColumnMeta]
    foreign_key: list[str] = []
    description: str = ""


class ClarificationPair(BaseModel):
    question: str
    answer: str


class QuerrySession(BaseModel):
    session_id: str
    original_question: str
    status: QueryStatus
    selected_tables: list[str] = []
    clarifications: list[ClarificationPair] = []
    pending_clarification_question: Optional[str] = None
    generated_sql: Optional[str] = None
    last_validation_error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)