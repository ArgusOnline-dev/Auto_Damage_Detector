#!/usr/bin/env python3
"""
Builds a YOLOv8-ready dataset (damage-only) from the fused annotations.

Each label corresponds to one of the normalized damage classes:
['dent','scratch','cracked','broken_part','missing_part','paint_chip','flaking','corrosion']
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


DAMAGE_CLASSES = [
    "dent",
    "scratch",
    "cracked",
    "broken_part",
    "missing_part",
    "paint_chip",
    "flaking",
    "corrosion",
    "intact",
]
CLASS_TO_ID = {name: idx for idx, name in enumerate(DAMAGE_CLASSES)}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build YOLOv8 dataset containing only damage classes."
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
        help="Fraction of samples to allocate to the training split.",
    )
    parser.add_argument(
        "--val-ratio",
        type=float,
        default=0.2,
        help="Fraction of samples for validation split (rest goes to test).",
    )
    parser.add_argument(
        "--min-damages-per-image",
        type=int,
        default=1,
        help="Minimum number of damage annotations required to include an image.",
    )
    parser.add_argument(
        "--balance-min-samples",
        type=int,
        default=0,
        help="If > 0, oversample classes until they have at least this many samples by duplicating images/labels.",
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
        img_dir = root / "images" / split
        lbl_dir = root / "labels" / split
        img_dir.mkdir(parents=True, exist_ok=True)
        lbl_dir.mkdir(parents=True, exist_ok=True)
        structure[f"images_{split}"] = img_dir
        structure[f"labels_{split}"] = lbl_dir
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
    min_damages_per_image: int,
    seed: int,
    balance_min_samples: int,
) -> Dict:
    output_root.mkdir(parents=True, exist_ok=True)
    splits = prepare_output_dirs(output_root)

    match_files = sorted(matches_dir.glob("*.json"))
    usable = []
    for path in match_files:
        data = load_matches(path)
        matches = [
            m for m in data.get("matches", [])
            if m.get("damage_type") in CLASS_TO_ID
        ]
        if len(matches) >= min_damages_per_image:
            usable.append({"image": data["image"], "matches": matches})

    if not usable:
        raise RuntimeError("No images met the minimum damage requirement.")

    random.Random(seed).shuffle(usable)
    total = len(usable)

    class_counts = Counter()

    class_files = {name: [] for name in DAMAGE_CLASSES}  # track files per class
    duplication_log = {name: 0 for name in DAMAGE_CLASSES}

    for idx, data in enumerate(tqdm(usable, desc="Writing damage-only dataset")):
        split = assign_split(idx, total, train_ratio, val_ratio)
        img_src = Path(data["image"])
        img_dst = splits[f"images_{split}"] / img_src.name
        shutil.copy2(img_src, img_dst)

        label_records = []
        per_class_counts_in_file = Counter()
        for match in data["matches"]:
            damage_type = match["damage_type"]
            cls_id = CLASS_TO_ID[damage_type]
            bbox = match["bbox_xywh_norm"]
            label_records.append((cls_id, bbox))
            class_counts[damage_type] += 1
            per_class_counts_in_file[damage_type] += 1

        label_path = splits[f"labels_{split}"] / (img_src.stem + ".txt")
        write_label_file(label_path, label_records)

        for damage_type, count in per_class_counts_in_file.items():
            class_files[damage_type].append(
                {
                    "split": split,
                    "image": img_dst,
                    "label": label_path,
                    "count": count,
                }
            )

    # Optional oversampling/balancing
    dup_summary = {}
    if balance_min_samples > 0:
        import random as _random
        rng = _random.Random(seed)
        for damage_type in DAMAGE_CLASSES:
            current = class_counts.get(damage_type, 0)
            if current == 0:
                continue  # nothing to duplicate
            while current < balance_min_samples and class_files[damage_type]:
                sample = rng.choice(class_files[damage_type])
                src_img = sample["image"]
                src_label = sample["label"]
                dup_idx = duplication_log[damage_type] + 1
                duplication_log[damage_type] = dup_idx

                new_img = src_img.with_name(src_img.stem + f"__dup{dup_idx}" + src_img.suffix)
                new_label = src_label.with_name(src_label.stem + f"__dup{dup_idx}" + src_label.suffix)

                shutil.copy2(src_img, new_img)
                shutil.copy2(src_label, new_label)

                class_counts[damage_type] += sample["count"]
                current = class_counts[damage_type]

                class_files[damage_type].append(
                    {
                        "split": sample["split"],
                        "image": new_img,
                        "label": new_label,
                        "count": sample["count"],
                    }
                )
                dup_summary.setdefault(damage_type, 0)
                dup_summary[damage_type] += 1

    # Write metadata files
    (output_root / "classes.txt").write_text("\n".join(DAMAGE_CLASSES))
    data_yaml = "\n".join(
        [
            f"path: {output_root.resolve()}",
            "train: images/train",
            "val: images/val",
            "test: images/test",
            f"nc: {len(DAMAGE_CLASSES)}",
            "names: [" + ", ".join(f"'{name}'" for name in DAMAGE_CLASSES) + "]",
        ]
    )
    (output_root / "data.yaml").write_text(data_yaml)

    stats = {
        "total_images": total,
        "class_distribution": dict(class_counts),
        "train_ratio": train_ratio,
        "val_ratio": val_ratio,
        "min_damages_per_image": min_damages_per_image,
        "classes": DAMAGE_CLASSES,
        "balance_min_samples": balance_min_samples,
        "duplications": dup_summary,
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
        min_damages_per_image=args.min_damages_per_image,
        seed=args.seed,
        balance_min_samples=args.balance_min_samples,
    )
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
