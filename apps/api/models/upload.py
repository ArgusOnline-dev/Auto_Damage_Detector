"""Pydantic models for upload requests and responses."""
from typing import List
from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    """Response model for file upload."""
    file_ids: List[str] = Field(..., description="List of uploaded file IDs")
    message: str = Field(default="Upload successful", description="Status message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "file_ids": ["uuid1", "uuid2", "uuid3"],
                "message": "Upload successful"
            }
        }

