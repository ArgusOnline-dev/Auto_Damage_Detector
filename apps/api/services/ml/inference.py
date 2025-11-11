"""ML inference service (placeholder until model is ready)."""
import uuid
from typing import List
from apps.api.models.detection import Detection
from apps.api.utils.file_handler import file_handler


def run_inference(file_ids: List[str]) -> dict:
    """
    Run ML inference on uploaded images (placeholder).
    
    Args:
        file_ids: List of file IDs to process
        
    Returns:
        Dictionary with image_id and detections
    """
    # Validate all files exist
    for file_id in file_ids:
        if not file_handler.file_exists(file_id):
            raise FileNotFoundError(file_id)
    
    # Mock detection results for testing
    # This will be replaced with actual YOLOv8 inference when model is ready
    mock_detections = []
    
    # Generate mock detections for each image
    for file_id in file_ids:
        # Mock detection 1: Door with dent
        mock_detections.append(Detection(
            part="door",
            damage_type="dent",
            confidence=0.85,
            bbox=[100.0, 200.0, 300.0, 400.0],
            severity=None
        ))
        
        # Mock detection 2: Front bumper with scrape
        mock_detections.append(Detection(
            part="front_bumper",
            damage_type="scrape",
            confidence=0.92,
            bbox=[50.0, 150.0, 250.0, 300.0],
            severity=None
        ))
    
    # Return results for first image (in real implementation, would return per image)
    return {
        "image_id": file_ids[0] if file_ids else str(uuid.uuid4()),
        "detections": mock_detections[:2]  # Return 2 mock detections
    }

