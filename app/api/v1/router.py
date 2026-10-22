from app.api.v1.endpoints import clarify
from fastapi import APIRouter
from app.api.v1.endpoints import query

router = APIRouter()
router.include_router(query.router,   prefix="/query",   tags=["Query"])
router.include_router(clarify.router, prefix="/clarify", tags=["Clarify"])