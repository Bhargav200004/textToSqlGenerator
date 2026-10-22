from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from app.models.request import QueryRequest
from app.models.response import QueryResponse
from app.core.dependencies import get_orchestrator
from app.core.orchestrator import QueryOrchestrator

router = APIRouter()

@router.post("", response_model=QueryResponse)
async def submit_query(
    body: QueryRequest,
    orchestrator: QueryOrchestrator = Depends(get_orchestrator)
) -> QueryResponse:
    logger.info(f"Query received | question: {body.question[:80]!r}")
    try:
        response = await orchestrator.handle_query(body)
        logger.info(f"Query done | status: {response.status} | session: {response.session_id}")
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in submit_query" , exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))