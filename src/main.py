import logging

import uvicorn
from fastapi import FastAPI

from src.core.config import settings
from src.routers import api_router

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Include routers
app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    logging.info(
        f"Navigate the url: http://{settings.HOST}:{settings.PORT}/docs for Swagger docs"
    )
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        workers=settings.WORKER_COUNT,
    )
