from app.services.clarification import ClarificationEngine
from app.services.validator import SQLValidator
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.services.schema import SchemaService
from app.services.llm import LLMService
from app.core.session import SessionManager
from app.core.orchestrator import QueryOrchestrator
from app.api.v1.router import router
from app.config import settings

import pprint


@asynccontextmanager
async def lifespan(app: FastAPI):
    schema_service = SchemaService(settings.schema_path)
    schema_service.load()
    llm_service = LLMService(settings)
    validator = SQLValidator(schema_service)
    clarification_engine = ClarificationEngine(
        llm_service
    )
    session_manager = SessionManager()
    orchestrator = QueryOrchestrator(
        llm=llm_service, schema=schema_service,
        clarification_engine=clarification_engine,
        validator=validator, session_manager=session_manager,
        config=settings
    )
    app.state.orchestrator = orchestrator
    app.state.schema_service = schema_service
    yield


app = FastAPI(title=settings.app_name , lifespan=lifespan)
app.include_router(router, prefix="/api/v1")
