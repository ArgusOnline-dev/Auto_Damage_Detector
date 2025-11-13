"""Utilities for loading YOLO models used by the inference service."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

from ultralytics import YOLO

from apps.api.core.config import settings


class ModelNotFoundError(RuntimeError):
    """Raised when a configured model file cannot be loaded."""


def _load_model(path: Path) -> YOLO:
    if not path.exists():
        raise ModelNotFoundError(f"Model weights not found: {path}")
    return YOLO(str(path))


@lru_cache(maxsize=1)
def get_part_detector() -> YOLO:
    """Return the cached Stage 1 part detector."""
    return _load_model(settings.PART_MODEL_PATH)


@lru_cache(maxsize=1)
def get_damage_detector() -> YOLO:
    """Return the cached Stage 2 damage detector."""
    return _load_model(settings.DAMAGE_MODEL_PATH)


def _format_prediction(result: Any, conf_threshold: float) -> List[Dict]:
    formatted: List[Dict] = []
    boxes = getattr(result, "boxes", None)
    names = getattr(result, "names", {})
    if boxes is None:
        return formatted

    for box in boxes:
        conf = float(box.conf)
        if conf < conf_threshold:
            continue
        cls_id = int(box.cls)
        label = names.get(cls_id, str(cls_id))
        xyxy = [float(v) for v in box.xyxy[0].tolist()]
        formatted.append(
            {
                "label": label,
                "confidence": conf,
                "bbox": xyxy,
            }
        )
    return formatted


def detect_parts(image_path: Path) -> List[Dict]:
    """Run Stage 1 detector on an image and return part predictions."""
    model = get_part_detector()
    results = model.predict(
        source=str(image_path),
        conf=settings.PART_CONF_THRESHOLD,
        device=settings.ML_DEVICE,
        verbose=False,
    )
    detections: List[Dict] = []
    for result in results:
        detections.extend(_format_prediction(result, settings.PART_CONF_THRESHOLD))
    return detections


def detect_damage(image_path: Path) -> List[Dict]:
    """Run Stage 2 detector on an image and return damage predictions."""
    model = get_damage_detector()
    results = model.predict(
        source=str(image_path),
        conf=settings.DAMAGE_CONF_THRESHOLD,
        device=settings.ML_DEVICE,
        verbose=False,
    )
    detections: List[Dict] = []
    for result in results:
        detections.extend(_format_prediction(result, settings.DAMAGE_CONF_THRESHOLD))
    return detections

