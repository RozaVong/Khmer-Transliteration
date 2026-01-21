from fastapi import APIRouter
from backend.api.v1.endpoints import router as endpoints_router

router = APIRouter()
router.include_router(endpoints_router, tags=["api"])