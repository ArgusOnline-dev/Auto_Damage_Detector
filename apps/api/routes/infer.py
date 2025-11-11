"""Inference route for ML inference (placeholder)."""
from fastapi import APIRouter, HTTPException
from apps.api.models.detection import InferenceRequest, InferenceResponse
from apps.api.services.ml.inference import run_inference
from apps.api.core.exceptions import FileNotFoundError

router = APIRouter(prefix="/infer", tags=["inference"])


@router.post("", response_model=InferenceResponse, status_code=200)
async def infer_damage(request: InferenceRequest):
    """
    Run ML inference on uploaded images (placeholder).
    
    Accepts file IDs from upload endpoint and returns detection results.
    Currently returns mock data until ML model is trained.
    """
    try:
        result = run_inference(request.file_ids)
        return InferenceResponse(**result)
    except FileNotFoundError as e:
        # FileNotFoundError is already an HTTPException with 404 status
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failed: {str(e)}")

