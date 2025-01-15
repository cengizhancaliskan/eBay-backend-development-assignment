import pytest
from fastapi import status
from fastapi.testclient import TestClient
from httpx import AsyncClient

from src.core.config import settings


def test_health_check(client: TestClient):
    response = client.get("/v1/status")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok", "version": settings.VERSION}


@pytest.mark.asyncio
async def test_status_endpoint(async_client: AsyncClient):
    response = await async_client.get("/v1/status")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok", "version": settings.VERSION}
