import json
from typing import Any, Optional

from fastapi import HTTPException, Query


def parse_image_hashes(
    image_hashes: Optional[list[str]] = Query(None),
) -> Optional[list[str]]:
    if image_hashes:
        return image_hashes
    return None


def parse_dataset_entities(
    dataset_entities: Optional[str] = Query(None),
) -> Any:
    try:
        if dataset_entities:
            return json.loads(dataset_entities)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400, detail="Invalid JSON format for dataset_entities"
        )
    return None


def parse_property_filters(
    property_filters: Optional[str] = Query(None),
) -> Any:
    try:
        if property_filters:
            return json.loads(property_filters)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400, detail="Invalid JSON format for property_filters"
        )
    return None
