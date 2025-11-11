"""Severity scoring interface for Saad's severity service."""
from typing import List
import random


def score_severity(detections: List[dict]) -> List[dict]:
    """
    Score severity for detections (placeholder).
    
    This is an interface for Saad's severity scoring service.
    When Saad implements the actual severity scoring (Step 6), this will call his service.
    
    Args:
        detections: List of detection results without severity
        
    Returns:
        List of detections with severity added
    """
    # Mock severity scoring for testing
    # This will be replaced with actual severity scoring when Saad's service is ready
    
    severity_levels = ["minor", "moderate", "severe"]
    
    # Add severity to each detection based on mock rules
    scored_detections = []
    for detection in detections:
        detection_copy = detection.copy()
        
        # Mock severity assignment based on damage type and confidence
        damage_type = detection.get("damage_type", "").lower()
        confidence = detection.get("confidence", 0.5)
        
        # Simple mock logic: higher confidence + certain damage types = higher severity
        if damage_type == "missing":
            detection_copy["severity"] = random.choice(["moderate", "severe"])
        elif damage_type == "crack":
            detection_copy["severity"] = random.choice(["minor", "moderate"])
        elif damage_type == "dent":
            detection_copy["severity"] = "moderate" if confidence > 0.8 else "minor"
        elif damage_type == "scrape":
            detection_copy["severity"] = "minor" if confidence > 0.7 else "moderate"
        else:
            detection_copy["severity"] = random.choice(severity_levels)
        
        scored_detections.append(detection_copy)
    
    return scored_detections

