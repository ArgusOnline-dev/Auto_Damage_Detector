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
    include_intact: bool = Field(default=True, description="Whether to include parts labeled intact")
    max_images: Optional[int] = Field(None, ge=1, description="Optional limit on number of images to process")
    
    class Config:
        json_schema_extra = {
            "example": {
                "file_ids": ["uuid1", "uuid2"],
                "include_intact": False,
                "max_images": 2
            }
        }


class InferenceImageResult(BaseModel):
    """Per-image inference result."""
    image_id: str = Field(..., description="Image ID")
    detections: List[Detection] = Field(..., description="List of detections for this image")

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


class InferenceResponse(BaseModel):
    """Response model for inference endpoint."""
    results: List[InferenceImageResult] = Field(..., description="Per-image inference results")
    include_intact: bool = Field(default=True, description="Whether intact detections are included")
    filtered_count: int = Field(default=0, description="Number of detections filtered out (e.g., intact)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "include_intact": True,
                "filtered_count": 0,
                "results": [
                    {
                        "image_id": "uuid1",
                        "detections": [
                            {
                                "part": "front_door",
                                "damage_type": "dent",
                                "confidence": 0.91,
                                "bbox": [120.0, 220.0, 360.0, 440.0],
                                "severity": None
                            }
                        ]
                    }
                ]
            }
        }

