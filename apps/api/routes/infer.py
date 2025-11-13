"""Inference route for ML inference."""
from fastapi import APIRouter, HTTPException
from apps.api.models.detection import InferenceRequest, InferenceResponse
from apps.api.services.ml.inference import run_inference
from apps.api.core.exceptions import FileNotFoundError

router = APIRouter(prefix="/infer", tags=["inference"])


@router.post("", response_model=InferenceResponse, status_code=200)
async def infer_damage(request: InferenceRequest):
    """
    Run ML inference on uploaded images.

    Accepts file IDs from upload endpoint and returns detection results.
    Supports optional filtering of intact parts and multiple images.
    """
    try:
        result = run_inference(
            file_ids=request.file_ids,
            include_intact=request.include_intact,
            max_images=request.max_images,
        )
        return InferenceResponse(**result)
    except FileNotFoundError as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failed: {str(e)}")

