from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from app.models.request import ClarifyRequest
from app.models.response import QueryResponse
from app.core.dependencies import get_orchestrator
from app.core.orchestrator import QueryOrchestrator

router = APIRouter()

@router.post("", response_model=QueryResponse)
async def submit_clarification(
    body: ClarifyRequest,
    orchestrator: QueryOrchestrator = Depends(get_orchestrator)
) -> QueryResponse:
    """
    Answer a clarification question from a previous /query response.

    Requires the session_id returned in the needs_clarification response.
    The session resumes from Stage 4 (SQL generation) — table search
    and clarification check are skipped entirely.

    Returns 404 if session_id is not found or has expired.
    """
    logger.info(f"Clarification received | session: {body.session_id}")
    try:
        response = await orchestrator.handle_clarify(body)
        logger.info(f"Clarification done | status: {response.status} | session: {body.session_id}")
        return response
    except HTTPException:
        raise  # 404 from SessionManager propagates as-is
    except Exception as e:
        logger.exception(f"Unexpected error in submit_clarification")
        raise HTTPException(status_code=500, detail=str(e))