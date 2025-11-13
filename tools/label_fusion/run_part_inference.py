#!/usr/bin/env python3
"""
Batch inference script that runs the existing part detector over the
damage dataset images and saves raw detections to JSON.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List

try:
    from tqdm import tqdm
except ImportError:  # Fallback when tqdm isn't installed
    def tqdm(iterable, **kwargs):
        return iterable

from ultralytics import YOLO


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run part detector on damage dataset images."
    )
    parser.add_argument(
        "--images-dir",
        required=True,
        type=Path,
        help="Directory containing damage dataset images.",
    )
    parser.add_argument(
        "--model-path",
        required=True,
        type=Path,
        help="Path to the trained part detector weights (YOLO .pt file).",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
        help="Directory where per-image detection JSON files will be written.",
    )
    parser.add_argument(
        "--device",
        default="0",
        help="Device for inference (e.g., '0' for GPU, 'cpu' for CPU).",
    )
    parser.add_argument(
        "--confidence-thresh",
        type=float,
        default=0.4,
        help="Minimum confidence required to keep a detection.",
    )
    parser.add_argument(
        "--max-images",
        type=int,
        default=None,
        help="Optional limit on number of images to process (for smoke tests).",
    )
    return parser.parse_args()


def run_inference(
    model: YOLO,
    image_paths: List[Path],
    output_dir: Path,
    conf_thresh: float,
    device: str,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    for img_path in tqdm(image_paths, desc="Running part inference"):
        out_path = output_dir / f"{img_path.stem}.json"
        if out_path.exists():
            continue  # Skip images we already processed

        results = model.predict(
            source=str(img_path),
            conf=conf_thresh,
            device=device,
            verbose=False,
        )
        detections = []
        for result in results:
            names = result.names
            boxes = result.boxes
            if boxes is None:
                continue
            for box in boxes:
                conf = float(box.conf)
                if conf < conf_thresh:
                    continue
                cls_id = int(box.cls)
                xyxy = [float(v) for v in box.xyxy[0].tolist()]
                detections.append(
                    {
                        "part": names.get(cls_id, str(cls_id)),
                        "confidence": conf,
                        "bbox_xyxy": xyxy,
                    }
                )

        out_path.write_text(json.dumps({"image": str(img_path), "detections": detections}, indent=2))


def main() -> None:
    args = parse_args()

    if not args.images_dir.exists():
        raise FileNotFoundError(f"Images directory not found: {args.images_dir}")
    if not args.model_path.exists():
        raise FileNotFoundError(f"Model weights not found: {args.model_path}")

    image_paths = sorted(
        [
            p
            for p in args.images_dir.iterdir()
            if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png"}
        ]
    )
    if args.max_images:
        image_paths = image_paths[: args.max_images]

    if not image_paths:
        raise RuntimeError("No images found to process.")

    model = YOLO(str(args.model_path))
    run_inference(
        model=model,
        image_paths=image_paths,
        output_dir=args.output_dir,
        conf_thresh=args.confidence_thresh,
        device=args.device,
    )


if __name__ == "__main__":
    main()
