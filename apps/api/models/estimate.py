"""Pydantic models for cost estimation."""
from typing import List
from pydantic import BaseModel, Field


class EstimateLineItem(BaseModel):
    """Single line item in cost estimate."""
    part: str = Field(..., description="Car part name")
    damage_type: str = Field(..., description="Type of damage")
    severity: str = Field(..., description="Severity level (minor, moderate, severe)")
    labor_hours: float = Field(..., ge=0, description="Labor hours required")
    labor_cost: float = Field(..., ge=0, description="Total labor cost")
    part_cost_new: float = Field(..., ge=0, description="New part cost")
    part_cost_used: float = Field(..., ge=0, description="Used part cost")
    total_new: float = Field(..., ge=0, description="Total cost with new part")
    total_used: float = Field(..., ge=0, description="Total cost with used part")
    
    class Config:
        json_schema_extra = {
            "example": {
                "part": "door",
                "damage_type": "dent",
                "severity": "moderate",
                "labor_hours": 5.4,
                "labor_cost": 810.0,
                "part_cost_new": 3500.0,
                "part_cost_used": 1750.0,
                "total_new": 4310.0,
                "total_used": 2560.0
            }
        }


class EstimateTotals(BaseModel):
    """Total costs for estimate."""
    min: float = Field(..., ge=0, description="Minimum total cost (using used parts)")
    likely: float = Field(..., ge=0, description="Likely total cost (using new parts)")
    max: float = Field(..., ge=0, description="Maximum total cost (with buffer)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "min": 2560.0,
                "likely": 4310.0,
                "max": 5000.0
            }
        }


class EstimateRequest(BaseModel):
    """Request model for estimate endpoint."""
    detections: List[dict] = Field(..., min_length=0, description="List of detection results")
    labor_rate: float = Field(default=150.0, ge=0, description="Labor rate per hour")
    use_oem_parts: bool = Field(default=True, description="Use OEM parts (True) or used parts (False)")
    car_type: str = Field(default="Super", description="Car type segment for cost rules (e.g., Super, Sedan)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "detections": [
                    {
                        "part": "door",
                        "damage_type": "dent",
                        "severity": "moderate",
                        "confidence": 0.85,
                        "bbox": [100.0, 200.0, 300.0, 400.0]
                    }
                ],
                "labor_rate": 150.0,
                "use_oem_parts": True,
                "car_type": "Super"
            }
        }


class EstimateResponse(BaseModel):
    """Response model for estimate endpoint."""
    line_items: List[EstimateLineItem] = Field(..., description="List of cost line items")
    totals: EstimateTotals = Field(..., description="Total costs")
    
    class Config:
        json_schema_extra = {
            "example": {
                "line_items": [
                    {
                        "part": "door",
                        "damage_type": "dent",
                        "severity": "moderate",
                        "labor_hours": 5.4,
                        "labor_cost": 810.0,
                        "part_cost_new": 3500.0,
                        "part_cost_used": 1750.0,
                        "total_new": 4310.0,
                        "total_used": 2560.0
                    }
                ],
                "totals": {
                    "min": 2560.0,
                    "likely": 4310.0,
                    "max": 5000.0
                }
            }
        }

