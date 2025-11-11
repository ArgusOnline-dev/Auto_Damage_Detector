"""Upload route for car photo uploads."""
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException
from apps.api.models.upload import UploadResponse
from apps.api.utils.file_handler import file_handler

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("", response_model=UploadResponse, status_code=200)
async def upload_files(files: List[UploadFile] = File(...)):
    """
    Upload car photos.
    
    Accepts multiple image files (JPEG/PNG) up to 10MB each.
    Returns file IDs for use in inference endpoint.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    try:
        file_ids = await file_handler.save_files(files)
        return UploadResponse(file_ids=file_ids, message="Upload successful")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

