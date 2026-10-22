from app.models.prompt_type import PROMPT_TYPE
from app.services.llm import LLMService
from dataclasses import dataclass


@dataclass
class ClarificationResult:
    needed: bool
    question: str | None = None


def parse_clarification_response(raw: str) -> ClarificationResult:
    needed, question = False, None
    for line in raw.strip().splitlines():
        if line.upper().startswith("NEEDS_CLARIFICATION:"):
            needed = "yes" in line.split(":", 1)[1].strip().lower()
        elif line.upper().startswith("QUESTION:"):
            value = line.split(":", 1)[1].strip()
            if value.upper() != "NONE" and value:
                question = value
    if needed and not question:
        question = "Could you provide more details about what you are looking for?"
    return ClarificationResult(needed=needed, question=question)


class ClarificationEngine:
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service

    async def check(self, question: str, schema_text: str) -> ClarificationResult:
        raw = await self.llm.generate(PROMPT_TYPE.CLARIFICATION, {
            "question" : question,
            "schema" : schema_text
        })
        return parse_clarification_response(raw)
