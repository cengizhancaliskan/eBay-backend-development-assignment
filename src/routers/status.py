from fastapi import APIRouter

from src.core.config import settings
from src.schemas.status import StatusResponse

router = APIRouter()


@router.get("", response_model=StatusResponse)
async def status() -> StatusResponse:
    """
    Health check endpoint for monitoring and load balancers.
    """
    return StatusResponse(status="ok", version=settings.VERSION)
