"""Estimate route for cost estimation."""
from fastapi import APIRouter, HTTPException
from apps.api.models.estimate import EstimateRequest, EstimateResponse
from apps.api.services.severity.interface import score_severity
from apps.api.services.cost_engine.interface import calculate_cost

router = APIRouter(prefix="/estimate", tags=["estimate"])


@router.post("", response_model=EstimateResponse, status_code=200)
async def estimate_cost(request: EstimateRequest):
    """
    Calculate repair cost estimate.
    
    Accepts detection results, applies severity scoring, and calculates costs.
    Uses placeholder services until Saad's cost engine and severity services are ready.
    """
    try:
        # Handle empty detections
        if not request.detections:
            from apps.api.models.estimate import EstimateTotals
            return EstimateResponse(
                line_items=[],
                totals=EstimateTotals(min=0.0, likely=0.0, max=0.0)
            )
        
        # Score severity for detections
        scored_detections = score_severity(request.detections)
        
        # Calculate costs
        result = calculate_cost(
            scored_detections,
            labor_rate=request.labor_rate,
            use_oem_parts=request.use_oem_parts
        )
        
        return EstimateResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cost estimation failed: {str(e)}")

