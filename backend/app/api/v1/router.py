"""Aggregation of v1 API routers."""

from fastapi import APIRouter
from .health import router as health_router
from .auth import router as auth_router
from .analyses import router as analyses_router

api_v1_router = APIRouter()
api_v1_router.include_router(health_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(analyses_router)
