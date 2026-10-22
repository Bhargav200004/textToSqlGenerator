from fastapi import Request

from app.config import Settings
from app.services.schema import SchemaService
from app.core.orchestrator import QueryOrchestrator



def get_orchestrator(request: Request) -> QueryOrchestrator:
    data = request.app.state.orchestrator
    return data

def get_schema_service(request: Request) -> SchemaService:
    return request.app.state.schema_service

def get_settings(request: Request) -> Settings:
    return request.app.state.orchestrator.config