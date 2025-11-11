"""Pydantic models for report generation."""
from typing import List
from pydantic import BaseModel, Field
from apps.api.models.detection import Detection
from apps.api.models.estimate import EstimateLineItem, EstimateTotals


class ReportData(BaseModel):
    """Complete report data model."""
    report_id: str = Field(..., description="Unique report ID")
    image_ids: List[str] = Field(..., description="List of processed image IDs")
    detections: List[Detection] = Field(..., description="All detections")
    line_items: List[EstimateLineItem] = Field(..., description="Cost estimate line items")
    totals: EstimateTotals = Field(..., description="Total costs")
    labor_rate: float = Field(..., description="Labor rate used")
    use_oem_parts: bool = Field(..., description="Whether OEM parts were used")
    
    class Config:
        json_schema_extra = {
            "example": {
                "report_id": "report-uuid-123",
                "image_ids": ["uuid1", "uuid2"],
                "detections": [],
                "line_items": [],
                "totals": {
                    "min": 0.0,
                    "likely": 0.0,
                    "max": 0.0
                },
                "labor_rate": 150.0,
                "use_oem_parts": True
            }
        }


class ReportPDFRequest(BaseModel):
    """Request model for PDF report generation."""
    report_data: ReportData = Field(..., description="Report data to generate PDF from")
    
    class Config:
        json_schema_extra = {
            "example": {
                "report_data": {
                    "report_id": "report-uuid-123",
                    "image_ids": ["uuid1"],
                    "detections": [],
                    "line_items": [],
                    "totals": {
                        "min": 0.0,
                        "likely": 0.0,
                        "max": 0.0
                    },
                    "labor_rate": 150.0,
                    "use_oem_parts": True
                }
            }
        }

