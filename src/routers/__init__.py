from fastapi import APIRouter

from src.routers import listing, status

api_router = APIRouter()

api_router.include_router(status.router)
api_router.include_router(listing.router)
