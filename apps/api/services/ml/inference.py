"""Two-stage ML inference service (part detector + damage detector)."""
from __future__ import annotations

import logging
from typing import Dict, List, Optional

from apps.api.core.config import settings
from apps.api.core.exceptions import FileNotFoundError as APIFileNotFoundError
import time

from apps.api.models.detection import Detection, InferenceImageResult
from apps.api.services.ml.model_loader import (
    detect_damage,
    detect_parts,
    ModelNotFoundError,
)
from apps.api.utils.file_handler import file_handler

logger = logging.getLogger(__name__)


def _canonicalize(label: str) -> str:
    return label.strip().lower().replace(" ", "_").replace("-", "_")


def _compute_iou(box_a: List[float], box_b: List[float]) -> float:
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b

    ix1 = max(ax1, bx1)
    iy1 = max(ay1, by1)
    ix2 = min(ax2, bx2)
    iy2 = min(ay2, by2)

    inter_w = max(0.0, ix2 - ix1)
    inter_h = max(0.0, iy2 - iy1)
    inter_area = inter_w * inter_h
    if inter_area <= 0:
        return 0.0

    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    union = area_a + area_b - inter_area
    if union <= 0:
        return 0.0
    return inter_area / union


def _match_damage_to_parts(
    parts: List[Dict],
    damages: List[Dict],
    iou_threshold: float,
) -> List[Detection]:
    """Assign the highest-confidence damage prediction to each part."""
    assignments: Dict[int, Dict[str, Optional[float]]] = {}
    for idx, part in enumerate(parts):
        assignments[idx] = {
            "damage_type": "intact",
            "confidence": part["confidence"],
        }

    for damage in damages:
        damage_label = _canonicalize(damage["label"])
        if damage_label == "intact":
            continue  # intact handled via fallback

        best_idx: Optional[int] = None
        best_iou = 0.0
        for idx, part in enumerate(parts):
            iou = _compute_iou(part["bbox"], damage["bbox"])
            if iou > best_iou:
                best_iou = iou
                best_idx = idx

        if best_idx is not None and best_iou >= iou_threshold:
            current_conf = assignments[best_idx]["confidence"] or 0.0
            if damage["confidence"] > current_conf:
                assignments[best_idx] = {
                    "damage_type": damage_label,
                    "confidence": damage["confidence"],
                }

    detections: List[Detection] = []
    for idx, part in enumerate(parts):
        assigned = assignments.get(idx, {"damage_type": "intact", "confidence": part["confidence"]})
        damage_type = assigned["damage_type"] or "intact"
        damage_conf = assigned["confidence"] or part["confidence"]
        final_conf = min(part["confidence"], damage_conf)
        detections.append(
            Detection(
                part=_canonicalize(part["label"]),
                damage_type=damage_type,
                confidence=final_conf,
                bbox=part["bbox"],
                severity=None,
            )
        )
    return detections


def _prepare_part_predictions(raw_predictions: List[Dict]) -> List[Dict]:
    prepared = []
    for pred in raw_predictions:
        prepared.append(
            {
                "label": _canonicalize(pred["label"]),
                "confidence": float(pred["confidence"]),
                "bbox": pred["bbox"],
            }
        )
    return prepared


def _prepare_damage_predictions(raw_predictions: List[Dict]) -> List[Dict]:
    prepared = []
    for pred in raw_predictions:
        prepared.append(
            {
                "label": _canonicalize(pred["label"]),
                "confidence": float(pred["confidence"]),
                "bbox": pred["bbox"],
            }
        )
    return prepared


def _process_image(image_path) -> List[Detection]:
    part_preds = _prepare_part_predictions(detect_parts(image_path))
    if not part_preds:
        logger.info("No parts detected for %s", image_path)
        return []

    damage_preds = _prepare_damage_predictions(detect_damage(image_path))
    return _match_damage_to_parts(
        part_preds,
        damage_preds,
        settings.DAMAGE_MATCH_MIN_IOU,
    )


def run_inference(
    file_ids: List[str],
    include_intact: bool = True,
    max_images: Optional[int] = None,
) -> dict:
    """
    Run two-stage ML inference on uploaded images.

    Args:
        file_ids: List of file IDs to process
        include_intact: Whether to include intact detections
        max_images: Optional limit on number of images to process

    Returns:
        Dictionary with image_id and detections
    """
    if not file_ids:
        return {"results": [], "include_intact": include_intact, "filtered_count": 0}

    processed = []
    filtered_count = 0

    limited_file_ids = file_ids[:max_images] if max_images else file_ids

    for image_id in limited_file_ids:
        if not file_handler.file_exists(image_id):
            raise APIFileNotFoundError(image_id)

        image_path = file_handler.get_file_path(image_id)

        start_time = time.perf_counter()
        try:
            detections = _process_image(image_path)
        except ModelNotFoundError as exc:
            logger.error("Inference failed: %s", exc)
            raise
        except Exception as exc:  # pragma: no cover
            logger.exception("Unexpected error during inference: %s", exc)
            raise
        latency_ms = (time.perf_counter() - start_time) * 1000

        if not include_intact:
            before = len(detections)
            detections = [d for d in detections if d.damage_type != "intact"]
            filtered_count += before - len(detections)

        logger.info(
            "Inference complete for %s (detections=%d, latency=%.2fms, include_intact=%s)",
            image_id,
            len(detections),
            latency_ms,
            include_intact,
        )

        processed.append(
            InferenceImageResult(
                image_id=image_id,
                detections=detections,
            )
        )

    return {
        "results": processed,
        "include_intact": include_intact,
        "filtered_count": filtered_count,
    }

