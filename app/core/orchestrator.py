from unittest import result
from app.core import session
from app.models.domain import ClarificationPair
from app.models.request import ClarifyRequest
from app.services.validator import SQLValidator
from app.services.clarification import ClarificationEngine
from app.models.prompt_type import PROMPT_TYPE
from loguru import logger
from app.core.parsers import parse_sql_response
from app.config import Settings
from app.models.response import QueryStatus
from app.models.response import QueryResponse
from app.core.parsers import parse_table_list
from app.services.schema import SchemaService
from app.services.llm import LLMService
from app.core.session import SessionManager
from app.models.request import QueryRequest


class QueryOrchestrator:
    def __init__(self, llm : LLMService , schema : SchemaService, clarification_engine: ClarificationEngine , validator : SQLValidator, session_manager : SessionManager, config : Settings):
        self.llm = llm
        self.schema = schema
        self.ce = clarification_engine
        self.validator = validator
        self.sm = session_manager
        self.config = config

    
    async def handle_query(self, request: QueryRequest) -> QueryRequest:
        session = self.sm.create(request.question)

        raw = await self.llm.generate(PROMPT_TYPE.TABLE_SELECTION , {
            "question" : request.question,
            "all_tables" : self.schema.get_all_table_names()
        })
        session.selected_tables = parese_data = parse_table_list(raw) 
        if not session.selected_tables:
            return QueryResponse(
                session_id=session.session_id,
                status=QueryStatus.ERROR,
                error_message="No relevant tables found for this question"
            )

        schema_text = self.schema.get_schema_text(session.selected_tables)

        result = await self.ce.check(request.question, schema_text)
        if result.needed:
            session.status = QueryStatus.NEED_CLARIFICATION
            session.pending_clarification_question = result.question
            self.sm.save(session)
            return QueryResponse(
                session_id=session.session_id,
                status=QueryStatus.NEED_CLARIFICATION,
                clarification_question=result.question
            )

        return await self._generate_and_validate(session)


    async def handle_clarify(self, request: ClarifyRequest) -> QueryResponse:
        session = self.sm.load(request.session_id)
        session.clarifications.append(ClarificationPair(
            question=session.pending_clarification_question or "",
            answer=request.answer
        ))
        return await self._generate_and_validate(session)

        
    async def _generate_and_validate(self, session) -> QueryResponse:
        schema_text = self.schema.get_schema_text(session.selected_tables)
        for attempt in range(self.config.max_retries + 1):
            raw = await self.llm.generate(PROMPT_TYPE.SQL_GENERATION , {
                "question" : session.original_question,
                "schema": schema_text,
                "clarifications": [c.dict() for c in session.clarifications],
                "validation_error": session.last_validation_error if attempt > 0 else None
            })

            sql , explanation = parse_sql_response(raw)
            if not sql:
                session.last_validation_error = "Model did not return SQL in expected format"
                continue

            result = self.validator.validate(sql , session.selected_tables)
            if result.valid:
                session.generated_sql = sql
                session.status = QueryStatus.SQL_READY
                self.sm.save(session)

                return QueryResponse(
                    session_id=session.session_id,
                    status=QueryStatus.SQL_READY,
                    sql=sql,
                    explanation=explanation,
                    tables_used=session.selected_tables
                )

            session.last_validation_error = result.error
            self.sm.save(session)
        return QueryResponse(
                session_id=session.session_id,
                status=QueryStatus.SQL_READY,
                sql=sql,
                explanation=explanation,
                tables_used=session.selected_tables
        )

