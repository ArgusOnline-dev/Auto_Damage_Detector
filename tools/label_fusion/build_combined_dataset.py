#!/usr/bin/env python3
"""
Builds a YOLOv8-ready dataset from fused part+damage annotations.
"""
from __future__ import annotations

import argparse
import json
import random
import shutil
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, **kwargs):
        return iterable


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert fused part+damage matches into a YOLOv8 dataset."
    )
    parser.add_argument(
        "--matches-dir",
        required=True,
        type=Path,
        help="Directory with JSON files produced by match_damage_to_parts.py.",
    )
    parser.add_argument(
        "--output-root",
        required=True,
        type=Path,
        help="Root directory for the generated dataset.",
    )
    parser.add_argument(
        "--train-ratio",
        type=float,
        default=0.7,
        help="Fraction of data to allocate to the training split.",
    )
    parser.add_argument(
        "--val-ratio",
        type=float,
        default=0.2,
        help="Fraction of data to allocate to the validation split (rest goes to test).",
    )
    parser.add_argument(
        "--min-matches",
        type=int,
        default=1,
        help="Minimum number of matches required for an image to be included.",
    )
    parser.add_argument(
        "--min-samples-per-class",
        type=int,
        default=25,
        help="Minimum number of samples per class. Classes below this threshold are mapped to '{part}_other_damage' fallback.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for deterministic splits.",
    )
    return parser.parse_args()


def load_matches(path: Path) -> Dict:
    return json.loads(path.read_text())


def prepare_output_dirs(root: Path) -> Dict[str, Path]:
    structure = {}
    for split in ("train", "val", "test"):
        structure[f"images_{split}"] = root / "images" / split
        structure[f"labels_{split}"] = root / "labels" / split
        structure[f"images_{split}"].mkdir(parents=True, exist_ok=True)
        structure[f"labels_{split}"].mkdir(parents=True, exist_ok=True)
    return structure


def assign_split(index: int, total: int, train_ratio: float, val_ratio: float) -> str:
    train_cutoff = int(total * train_ratio)
    val_cutoff = train_cutoff + int(total * val_ratio)
    if index < train_cutoff:
        return "train"
    if index < val_cutoff:
        return "val"
    return "test"


def write_label_file(label_path: Path, records: List[Tuple[int, List[float]]]) -> None:
    lines = []
    for cls_id, bbox in records:
        bbox_str = " ".join(f"{v:.6f}" for v in bbox)
        lines.append(f"{cls_id} {bbox_str}")
    label_path.write_text("\n".join(lines))


def build_dataset(
    matches_dir: Path,
    output_root: Path,
    train_ratio: float,
    val_ratio: float,
    min_matches: int,
    min_samples_per_class: int,
    seed: int,
) -> Dict:
    output_root.mkdir(parents=True, exist_ok=True)
    splits = prepare_output_dirs(output_root)

    match_files = sorted(matches_dir.glob("*.json"))
    usable = []
    for path in match_files:
        data = load_matches(path)
        if len(data.get("matches", [])) >= min_matches:
            usable.append(data)

    random.Random(seed).shuffle(usable)
    total = len(usable)
    if total == 0:
        raise RuntimeError("No images with matches were found. Check inputs.")

    # First pass: count all classes
    all_class_counts = Counter()
    for data in usable:
        for match in data["matches"]:
            all_class_counts[match["combined_class"]] += 1
    
    # Build class mapping with pruning
    class_mapping = {}  # original_class -> final_class
    final_classes = set()
    pruned_classes = []
    
    for class_name, count in all_class_counts.items():
        if count >= min_samples_per_class:
            # Keep the class as-is
            class_mapping[class_name] = class_name
            final_classes.add(class_name)
        else:
            # Map to fallback: extract part name and use "{part}_other_damage"
            # Format is typically "{part}_{damage_type}"
            parts = class_name.rsplit("_", 1)
            if len(parts) == 2:
                part_name = parts[0]
                fallback_class = f"{part_name}_other_damage"
                class_mapping[class_name] = fallback_class
                final_classes.add(fallback_class)
                pruned_classes.append((class_name, count, fallback_class))
            else:
                # Can't parse, keep as-is but log
                class_mapping[class_name] = class_name
                final_classes.add(class_name)
                pruned_classes.append((class_name, count, class_name))
    
    # Create final class list and mapping
    class_names = sorted(final_classes)
    class_to_id = {name: idx for idx, name in enumerate(class_names)}
    
    # Re-count after pruning
    class_counts = Counter()
    pruned_counts = Counter()  # Track how many samples went to each fallback
    
    for idx, data in enumerate(tqdm(usable, desc="Writing YOLO dataset")):
        split = assign_split(idx, total, train_ratio, val_ratio)
        img_src = Path(data["image"])
        img_dst = splits[f"images_{split}"] / img_src.name
        shutil.copy2(img_src, img_dst)

        label_records = []
        for match in data["matches"]:
            original_class = match["combined_class"]
            final_class = class_mapping[original_class]
            
            cls_id = class_to_id[final_class]
            bbox = match["bbox_xywh_norm"]
            label_records.append((cls_id, bbox))
            
            class_counts[final_class] += 1
            if original_class != final_class:
                pruned_counts[final_class] += 1

        label_path = splits[f"labels_{split}"] / (img_src.stem + ".txt")
        write_label_file(label_path, label_records)

    # Write metadata
    (output_root / "classes.txt").write_text("\n".join(class_names))
    data_yaml_str = "\n".join(
        [
            f"path: {output_root.resolve()}",
            "train: images/train",
            "val: images/val",
            "test: images/test",
            f"nc: {len(class_names)}",
            "names: [" + ", ".join(f"'{name}'" for name in class_names) + "]",
        ]
    )
    (output_root / "data.yaml").write_text(data_yaml_str)
    
    # Calculate before/after stats
    before_class_count = len(all_class_counts)
    after_class_count = len(class_names)
    pruned_class_count = len([c for c, _, _ in pruned_classes if class_mapping.get(c, c) != c])
    
    stats = {
        "total_images": total,
        "class_distribution": dict(class_counts),
        "train_ratio": train_ratio,
        "val_ratio": val_ratio,
        "min_matches": min_matches,
        "min_samples_per_class": min_samples_per_class,
        "pruning_stats": {
            "before_class_count": before_class_count,
            "after_class_count": after_class_count,
            "pruned_class_count": pruned_class_count,
            "pruned_classes": [
                {
                    "original": orig,
                    "count": cnt,
                    "mapped_to": mapped
                }
                for orig, cnt, mapped in pruned_classes
                if class_mapping.get(orig, orig) != orig
            ],
            "pruned_samples_by_fallback": dict(pruned_counts),
        }
    }
    (output_root / "stats.json").write_text(json.dumps(stats, indent=2))
    return stats


def main() -> None:
    args = parse_args()
    stats = build_dataset(
        matches_dir=args.matches_dir,
        output_root=args.output_root,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        min_matches=args.min_matches,
        min_samples_per_class=args.min_samples_per_class,
        seed=args.seed,
    )
    print(json.dumps(stats, indent=2, default=int))


if __name__ == "__main__":
    main()
