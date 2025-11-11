"""Pydantic models for detection results."""
from typing import List, Optional
from pydantic import BaseModel, Field


class Detection(BaseModel):
    """Single detection result."""
    part: str = Field(..., description="Detected car part (e.g., 'door', 'bumper')")
    damage_type: str = Field(..., description="Type of damage (dent, scrape, crack, missing, intact)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")
    bbox: List[float] = Field(..., min_length=4, max_length=4, description="Bounding box [x1, y1, x2, y2]")
    severity: Optional[str] = Field(None, description="Severity level (minor, moderate, severe)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "part": "door",
                "damage_type": "dent",
                "confidence": 0.85,
                "bbox": [100.0, 200.0, 300.0, 400.0],
                "severity": None
            }
        }


class InferenceRequest(BaseModel):
    """Request model for inference endpoint."""
    file_ids: List[str] = Field(..., min_length=1, description="List of file IDs to process")
    
    class Config:
        json_schema_extra = {
            "example": {
                "file_ids": ["uuid1", "uuid2"]
            }
        }


class InferenceResponse(BaseModel):
    """Response model for inference endpoint."""
    image_id: str = Field(..., description="Image ID")
    detections: List[Detection] = Field(..., description="List of detections")
    
    class Config:
        json_schema_extra = {
            "example": {
                "image_id": "uuid1",
                "detections": [
                    {
                        "part": "door",
                        "damage_type": "dent",
                        "confidence": 0.85,
                        "bbox": [100.0, 200.0, 300.0, 400.0],
                        "severity": None
                    }
                ]
            }
        }

