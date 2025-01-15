from fastapi import APIRouter

from src.routers import status

api_router = APIRouter()

api_router.include_router(status.router, prefix="/status")
