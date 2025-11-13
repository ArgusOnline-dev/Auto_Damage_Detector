"""Severity scoring rules."""
from typing import List

from apps.api.core.config import settings


def _normalize_severity(value: str) -> str:
    if not value:
        return ""
    return value.strip().lower()


def _map_severity(damage_type: str, confidence: float) -> str:
    dt = (damage_type or "").lower()
    conf = confidence or 0.0

    if dt in {"missing_part", "missing", "broken_part"}:
        return "severe"
    if dt == "cracked" or dt == "crack":
        if conf >= 0.8:
            return "severe"
        if conf >= 0.5:
            return "moderate"
        return "minor"
    if dt == "dent":
        if conf >= 0.85:
            return "severe"
        if conf >= 0.5:
            return "moderate"
        return "minor"
    if dt in {"scratch", "paint_chip", "flaking", "corrosion", "scrape"}:
        if conf >= 0.7:
            return "moderate"
        return "minor"
    return "minor"


def score_severity(detections: List[dict]) -> List[dict]:
    """
    Score severity for detections using deterministic rules.

    Args:
        detections: List of detection results. Each detection must include `damage_type`
                    and optionally `severity` (user override) and `confidence`.

    Returns:
        List of detections with severity added/normalized.
    """
    scored: List[dict] = []
    for detection in detections:
        entry = detection.copy()
        existing = _normalize_severity(entry.get("severity", ""))
        if existing in {"minor", "moderate", "severe"}:
            entry["severity"] = existing
        else:
            damage_type = entry.get("damage_type", "")
            confidence = entry.get("confidence") or 0.0
            severity = _map_severity(damage_type, confidence)
            entry["severity"] = severity
        scored.append(entry)
    return scored

