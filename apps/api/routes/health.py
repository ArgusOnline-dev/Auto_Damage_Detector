"""Health check route."""
from fastapi import APIRouter
from pydantic import BaseModel
from apps.api.core.config import settings

router = APIRouter(prefix="/health", tags=["health"])


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    version: str


@router.get("", response_model=HealthResponse, status_code=200)
async def health_check():
    """
    Health check endpoint.
    
    Returns API status and version.
    """
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION
    )

