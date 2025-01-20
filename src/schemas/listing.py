from datetime import datetime
from typing import Any, Optional, Union

from fastapi import Depends
from pydantic import BaseModel, ConfigDict, Field

from src.schemas.dependency import (
    parse_dataset_entities,
    parse_image_hashes,
    parse_property_filters,
)


class PropertySchema(BaseModel):
    name: str
    type: str  # "str" or "bool"
    value: Union[str, bool]


class EntitySchema(BaseModel):
    name: str
    data: dict[str, Any]


class ListingResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    listing_id: str
    scan_date: datetime
    is_active: bool
    dataset_entity_ids: list[int]
    image_hashes: list[str]
    properties: list[PropertySchema]
    entities: list[EntitySchema]


class ListingFilterSchema(BaseModel):
    page: int = Field(ge=1, default=1)
    page_size: Optional[int] = Field(ge=1, le=100, default=None)
    listing_id: Optional[str] = None
    scan_date_from: Optional[datetime] = None
    scan_date_to: Optional[datetime] = None
    is_active: Optional[bool] = None
    image_hashes: Optional[list[str]] = Depends(parse_image_hashes)
    dataset_entities: Optional[dict[str, Any]] = Depends(parse_dataset_entities)
    property_filters: Optional[dict[str, Any]] = Depends(parse_property_filters)


class ListingResponse(BaseModel):
    listings: list[ListingResponseSchema]
    total: int


class PropertyCreateOrUpdateSchema(BaseModel):
    name: str
    type: str
    value: Union[str, bool]


class EntityCreateOrUpdateSchema(BaseModel):
    name: str
    data: dict[str, Any]


class ListingCreateOrUpdateSchema(BaseModel):
    listing_id: str
    scan_date: datetime
    is_active: bool
    image_hashes: list[str]
    properties: list[PropertyCreateOrUpdateSchema]
    entities: list[EntityCreateOrUpdateSchema]


class ListingsCreateOrUpdateSchema(BaseModel):
    listings: list[ListingCreateOrUpdateSchema]


class ListingCreateOrUpdateResponse(BaseModel):
    success: bool
    message: str
    created_count: int
    updated_count: int
    errors: Optional[list[str]] = None
