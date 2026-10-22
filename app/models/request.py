from pydantic import BaseModel , Field
from typing import Optional

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3 , max_length=1000)
    session_id : Optional[str] = None


class ClarifyRequest(BaseModel):
    session_id : str
    answer: str = Field(... , min_length=1 , max_length=2000)