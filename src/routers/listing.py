from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.base import get_db
from src.repositories.listing_repository import ListingRepository
from src.schemas.listing import (
    ListingCreateOrUpdateResponse,
    ListingFilterSchema,
    ListingResponse,
    ListingsCreateOrUpdateSchema,
)
from src.services.listing_service import ListingService

router = APIRouter(prefix="/listings", tags=["listings"])


@router.get("", response_model=ListingResponse)
async def get_listings(
    filters: ListingFilterSchema = Depends(), db: AsyncSession = Depends(get_db)
) -> ListingResponse:
    try:
        repository = ListingRepository(db)
        service = ListingService(repository)

        return await service.get_listings(filters)
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("", response_model=ListingCreateOrUpdateResponse)
async def create_or_update_listings(
    data: ListingsCreateOrUpdateSchema, db: AsyncSession = Depends(get_db)
) -> ListingCreateOrUpdateResponse:
    try:
        repository = ListingRepository(db)
        service = ListingService(repository)

        return await service.create_or_update_listings(data)
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))
