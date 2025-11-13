#!/usr/bin/env python3
"""
Matches damage polygons from the Supervisely export with detected parts
to create combined part+damage annotations.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

from PIL import Image
try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, **kwargs):
        return iterable


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fuse damage polygons with detected parts to produce combined labels."
    )
    parser.add_argument(
        "--damage-annotations",
        required=True,
        type=Path,
        help="Directory with Supervisely JSON annotation files (damage classes).",
    )
    parser.add_argument(
        "--damage-images",
        required=True,
        type=Path,
        help="Directory with raw damage dataset images (mirrors annotation names).",
    )
    parser.add_argument(
        "--part-detections",
        required=True,
        type=Path,
        help="Directory with per-image part detection JSON files from run_part_inference.py.",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
        help="Directory to store per-image fused annotation JSON files.",
    )
    parser.add_argument(
        "--iou-threshold",
        type=float,
        default=0.10,
        help="Minimum IoU between damage polygon bbox and part detection to consider a match.",
    )
    parser.add_argument(
        "--min-part-confidence",
        type=float,
        default=0.5,
        help="Minimum confidence threshold for part detections. Weak detections below this are ignored.",
    )
    parser.add_argument(
        "--fallback-min-iou",
        type=float,
        default=0.05,
        help="Minimum IoU required when using 'center inside' fallback matching.",
    )
    return parser.parse_args()


@dataclass
class Box:
    x1: float
    y1: float
    x2: float
    y2: float

    def area(self) -> float:
        return max(0.0, self.x2 - self.x1) * max(0.0, self.y2 - self.y1)

    def iou(self, other: "Box") -> float:
        ix1 = max(self.x1, other.x1)
        iy1 = max(self.y1, other.y1)
        ix2 = min(self.x2, other.x2)
        iy2 = min(self.y2, other.y2)
        inter = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
        union = self.area() + other.area() - inter
        return inter / union if union else 0.0

    def to_xywh_norm(self, width: int, height: int) -> Tuple[float, float, float, float]:
        cx = (self.x1 + self.x2) / 2.0
        cy = (self.y1 + self.y2) / 2.0
        w = self.x2 - self.x1
        h = self.y2 - self.y1
        return (
            cx / width,
            cy / height,
            w / width,
            h / height,
        )


def polygon_to_box(points: List[List[float]]) -> Box:
    xs = [pt[0] for pt in points]
    ys = [pt[1] for pt in points]
    return Box(min(xs), min(ys), max(xs), max(ys))


def canonicalize(label: str) -> str:
    return label.strip().lower().replace(" ", "_").replace("-", "_")


# Normalize damage labels to a standard set
DAMAGE_NORMALIZATION = {
    # Direct mappings
    "dent": "dent",
    "dents": "dent",
    "ding": "dent",
    "dings": "dent",
    "scratch": "scratch",
    "scratches": "scratch",
    "scrape": "scratch",
    "scrapes": "scratch",
    "cracked": "cracked",
    "crack": "cracked",
    "cracks": "cracked",
    "broken_part": "broken_part",
    "broken": "broken_part",
    "break": "broken_part",
    "missing_part": "missing_part",
    "missing": "missing_part",
    "paint_chip": "paint_chip",
    "paint_chips": "paint_chip",
    "chip": "paint_chip",
    "chips": "paint_chip",
    "flaking": "flaking",
    "flake": "flaking",
    "flakes": "flaking",
    "corrosion": "corrosion",
    "rust": "corrosion",
    "rusty": "corrosion",
}

VALID_DAMAGE_TYPES = {
    "dent", "scratch", "cracked", "broken_part", "missing_part",
    "paint_chip", "flaking", "corrosion", "intact"
}


def normalize_damage_label(label: str) -> str:
    """
    Normalize damage labels to a standard set of 8 types.
    Returns the normalized label or None if it should be dropped.
    """
    canonical = canonicalize(label)
    
    # Direct lookup
    if canonical in DAMAGE_NORMALIZATION:
        return DAMAGE_NORMALIZATION[canonical]
    
    # Try partial matches
    for key, value in DAMAGE_NORMALIZATION.items():
        if key in canonical or canonical in key:
            return value
    
    # If no match found, try to infer from common patterns
    if "dent" in canonical or "ding" in canonical:
        return "dent"
    if "scratch" in canonical or "scrape" in canonical:
        return "scratch"
    if "crack" in canonical:
        return "cracked"
    if "broken" in canonical or "break" in canonical:
        return "broken_part"
    if "missing" in canonical:
        return "missing_part"
    if "chip" in canonical or "paint" in canonical:
        return "paint_chip"
    if "flake" in canonical:
        return "flaking"
    if "corrosion" in canonical or "rust" in canonical:
        return "corrosion"
    
    # If we can't map it, return None to drop it
    return None


def load_part_detections(path: Path) -> List[Dict]:
    if not path.exists():
        return []
    data = json.loads(path.read_text())
    return data.get("detections", [])


def fuse_annotations(
    damage_ann_dir: Path,
    damage_img_dir: Path,
    part_det_dir: Path,
    output_dir: Path,
    iou_threshold: float,
    min_part_confidence: float,
    fallback_min_iou: float,
) -> Dict[str, int]:
    output_dir.mkdir(parents=True, exist_ok=True)
    stats = {"matched": 0, "unmatched_damage": 0, "unmatched_parts": 0}

    ann_files = sorted(p for p in damage_ann_dir.glob("*.json"))
    for ann_file in tqdm(ann_files, desc="Matching damage to parts"):
        # Annotation files are like "Car damages 101.png.json", stem is "Car damages 101.png"
        # But detection files are "Car damages 101.json", so we need to remove image extension
        image_name_with_ext = ann_file.stem  # e.g., "Car damages 101.png"
        # Remove image extension (.png, .jpg, etc.) to get base name
        image_name = Path(image_name_with_ext).stem  # e.g., "Car damages 101"
        detections = load_part_detections(part_det_dir / f"{image_name}.json")
        # Also try with the original image name with extension for image lookup
        img_candidates = list(damage_img_dir.glob(f"{image_name}.*"))
        if not img_candidates:
            # Fallback: try with the full annotation stem (in case image has different extension)
            img_candidates = list(damage_img_dir.glob(f"{image_name_with_ext}.*"))
        if not img_candidates:
            continue
        img_path = img_candidates[0]
        width, height = Image.open(img_path).size

        ann_data = json.loads(ann_file.read_text())
        damage_objs = ann_data.get("objects", [])

        matches = []
        unmatched_damage = []

        # Filter part detections by confidence threshold
        part_boxes = []
        for det in detections:
            if det["confidence"] < min_part_confidence:
                continue  # Skip weak detections
            bbox = Box(*det["bbox_xyxy"])
            part_boxes.append(
                {
                    "bbox": bbox,
                    "part": canonicalize(det["part"]),
                    "confidence": det["confidence"],
                }
            )

        # Allow multiple damages per part - removed used_part_indices constraint
        # This allows the same part to be matched with multiple damage annotations
        # (e.g., multiple scratches on the same door panel)
        matched_part_indices = set()  # Track which parts got matched (for stats only)

        for dmg in damage_objs:
            raw_dmg_label = dmg.get("classTitle", "unknown")
            # Normalize damage label to standard set
            dmg_label = normalize_damage_label(raw_dmg_label)
            if dmg_label is None:
                # Skip unmappable damage types
                unmatched_damage.append(raw_dmg_label)
                stats["unmatched_damage"] += 1
                continue
            
            points = dmg.get("points", {}).get("exterior", [])
            if len(points) < 2:
                continue
            dmg_box = polygon_to_box(points)
            # Calculate damage center for fallback matching
            dmg_center_x = (dmg_box.x1 + dmg_box.x2) / 2.0
            dmg_center_y = (dmg_box.y1 + dmg_box.y2) / 2.0
            
            best_idx = None
            best_iou = 0.0
            best_confidence = 0.0

            # Find the best matching part for this damage (can reuse parts)
            for idx, part in enumerate(part_boxes):
                iou = dmg_box.iou(part["bbox"])
                # Fallback: check if damage center is inside part bbox
                contains_center = (
                    part["bbox"].x1 <= dmg_center_x <= part["bbox"].x2 and
                    part["bbox"].y1 <= dmg_center_y <= part["bbox"].y2
                )
                
                # Prefer higher IoU matches
                is_match = False
                if iou >= iou_threshold:
                    # Primary match: IoU meets threshold
                    is_match = True
                elif contains_center and iou >= fallback_min_iou and part["confidence"] >= min_part_confidence:
                    # Fallback match: center inside AND IoU >= fallback_min_iou AND confidence >= threshold
                    is_match = True
                
                if is_match and (iou > best_iou or (iou == best_iou and part["confidence"] > best_confidence)):
                    best_iou = iou
                    best_idx = idx
                    best_confidence = part["confidence"]

            # Match if we found a valid part
            if best_idx is not None:
                part = part_boxes[best_idx]
                combo = f"{part['part']}_{dmg_label}"
                matches.append(
                    {
                        "combined_class": combo,
                        "part": part["part"],
                        "damage_type": dmg_label,
                        "confidence": part["confidence"],
                        "bbox_xyxy": [
                            dmg_box.x1,
                            dmg_box.y1,
                            dmg_box.x2,
                            dmg_box.y2,
                        ],
                        "bbox_xywh_norm": list(dmg_box.to_xywh_norm(width, height)),
                    }
                )
                matched_part_indices.add(best_idx)  # Track for stats only
                stats["matched"] += 1
            else:
                unmatched_damage.append(raw_dmg_label)
                stats["unmatched_damage"] += 1

        # Count unmatched parts (parts that never got matched to any damage)
        # Treat remaining unmatched parts as "intact" regions
        unmatched_parts = []
        for idx, part in enumerate(part_boxes):
            if idx in matched_part_indices:
                continue
            unmatched_parts.append(part["part"])
            bbox = part["bbox"]
            matches.append(
                {
                    "combined_class": f"{part['part']}_intact",
                    "part": part["part"],
                    "damage_type": "intact",
                    "confidence": part["confidence"],
                    "bbox_xyxy": [
                        bbox.x1,
                        bbox.y1,
                        bbox.x2,
                        bbox.y2,
                    ],
                    "bbox_xywh_norm": list(bbox.to_xywh_norm(width, height)),
                }
            )
            stats["matched"] += 1
        stats["unmatched_parts"] += len(unmatched_parts)

        out_payload = {
            "image": str(img_path),
            "width": width,
            "height": height,
            "matches": matches,
            "unmatched_damage": unmatched_damage,
            "unmatched_parts": unmatched_parts,
        }
        (output_dir / f"{image_name}.json").write_text(json.dumps(out_payload, indent=2))

    return stats


def main() -> None:
    args = parse_args()
    stats = fuse_annotations(
        damage_ann_dir=args.damage_annotations,
        damage_img_dir=args.damage_images,
        part_det_dir=args.part_detections,
        output_dir=args.output_dir,
        iou_threshold=args.iou_threshold,
        min_part_confidence=args.min_part_confidence,
        fallback_min_iou=args.fallback_min_iou,
    )
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
