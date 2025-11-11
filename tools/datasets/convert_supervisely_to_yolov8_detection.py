import argparse
import json
import random
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

from PIL import Image


@dataclass
class AnnotationObject:
    class_title: str
    # Polygons are lists of [x, y] points; we convert to bbox
    polygon: List[Tuple[float, float]]


def read_supervisely_annotation(json_path: Path) -> List[AnnotationObject]:
    with json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    objects = []
    for obj in data.get("objects", []):
        if obj.get("geometryType") != "polygon":
            # Skip non-polygon geometries for detection export
            continue
        points = obj.get("points", {}).get("exterior", [])
        if not points:
            continue
        # Ensure tuples of floats
        polygon = [(float(x), float(y)) for x, y in points]
        class_title = obj.get("classTitle", "unknown").strip()
        objects.append(AnnotationObject(class_title=class_title, polygon=polygon))
    return objects


def polygon_to_bbox(polygon: List[Tuple[float, float]]) -> Tuple[float, float, float, float]:
    xs = [p[0] for p in polygon]
    ys = [p[1] for p in polygon]
    x_min = min(xs)
    x_max = max(xs)
    y_min = min(ys)
    y_max = max(ys)
    return x_min, y_min, x_max, y_max


def bbox_to_yolo_line(
    cls_id: int,
    bbox: Tuple[float, float, float, float],
    img_w: int,
    img_h: int,
) -> str:
    x_min, y_min, x_max, y_max = bbox
    # Clamp to image bounds just in case
    x_min = max(0.0, min(x_min, img_w - 1))
    y_min = max(0.0, min(y_min, img_h - 1))
    x_max = max(0.0, min(x_max, img_w - 1))
    y_max = max(0.0, min(y_max, img_h - 1))

    w = max(0.0, x_max - x_min)
    h = max(0.0, y_max - y_min)
    if w <= 0 or h <= 0:
        return ""
    cx = x_min + w / 2.0
    cy = y_min + h / 2.0
    # Normalize
    return f"{cls_id} {cx / img_w:.6f} {cy / img_h:.6f} {w / img_w:.6f} {h / img_h:.6f}"


def gather_items(ann_dir: Path, img_dir: Path) -> List[Tuple[Path, Path]]:
    """
    Returns list of (annotation_json_path, image_path) pairs matched by basename.
    Supervisely files look like 'Car damages 114.jpg' with JSON 'Car damages 114.jpg.json'
    """
    pairs: List[Tuple[Path, Path]] = []
    ann_files = sorted([p for p in ann_dir.glob("*.json") if p.is_file()])
    # Build image lookup by full filename (with extension)
    image_index: Dict[str, Path] = {}
    for ext in ["*.jpg", "*.jpeg", "*.png", "*.JPG", "*.PNG", "*.JPEG"]:
        for p in img_dir.glob(ext):
            image_index[p.name] = p
    for ann in ann_files:
        # drop trailing '.json'
        image_filename = ann.name[:-5]  # remove ".json"
        img_path = image_index.get(image_filename)
        if img_path is None:
            # try alternative: some exports might mismatch casing/spacing
            continue
        pairs.append((ann, img_path))
    return pairs


def write_split_lists(items: List[Tuple[Path, Path]], split: Tuple[float, float, float]):
    train_ratio, val_ratio, test_ratio = split
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6
    n = len(items)
    n_train = int(n * train_ratio)
    n_val = int(n * val_ratio)
    train_items = items[:n_train]
    val_items = items[n_train : n_train + n_val]
    test_items = items[n_train + n_val :]
    return train_items, val_items, test_items


def ensure_clean_dir(path: Path):
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def convert_dataset(
    source_root: Path,
    out_root: Path,
    dataset_name: str,
    split: Tuple[float, float, float] = (0.7, 0.2, 0.1),
    seed: int = 42,
):
    """
    Convert a Supervisely-style dataset at:
      source_root/{dataset_name}/File1/{img,ann,...}
    into YOLOv8 detection format under:
      out_root/{images,labels}/{train,val,test}
      out_root/data.yaml
    """
    random.seed(seed)
    ds_root = source_root / dataset_name / "File1"
    ann_dir = ds_root / "ann"
    img_dir = ds_root / "img"
    if not ann_dir.is_dir() or not img_dir.is_dir():
        raise RuntimeError(f"Could not find ann/img folders under: {ds_root}")

    pairs = gather_items(ann_dir, img_dir)
    if not pairs:
        raise RuntimeError("No matched (annotation, image) pairs found.")
    random.shuffle(pairs)

    # First pass: collect class titles
    class_titles: Dict[str, int] = {}
    for ann_path, _ in pairs:
        objs = read_supervisely_annotation(ann_path)
        for obj in objs:
            if obj.class_title not in class_titles:
                class_titles[obj.class_title] = 0
    # Assign stable class ids alphabetically for reproducibility
    classes_sorted = sorted(class_titles.keys())
    title_to_id = {t: i for i, t in enumerate(classes_sorted)}

    # Prepare output directories
    images_root = out_root / "images"
    labels_root = out_root / "labels"
    for split_name in ["train", "val", "test"]:
        ensure_clean_dir(images_root / split_name)
        ensure_clean_dir(labels_root / split_name)

    # Split
    train_items, val_items, test_items = write_split_lists(pairs, split)
    splits = [("train", train_items), ("val", val_items), ("test", test_items)]

    # Convert and copy
    for split_name, items in splits:
        for ann_path, img_path in items:
            # Load annotations
            objs = read_supervisely_annotation(ann_path)
            # Get image size for normalization
            with Image.open(img_path) as im:
                w, h = im.size
            yolo_lines: List[str] = []
            for obj in objs:
                cls_id = title_to_id.get(obj.class_title)
                if cls_id is None:
                    continue
                bbox = polygon_to_bbox(obj.polygon)
                line = bbox_to_yolo_line(cls_id, bbox, w, h)
                if line:
                    yolo_lines.append(line)
            # Skip images without valid objects
            if not yolo_lines:
                continue
            # Write label
            out_img_path = images_root / split_name / img_path.name
            out_lbl_path = labels_root / split_name / (img_path.stem + ".txt")
            shutil.copy2(img_path, out_img_path)
            out_lbl_path.write_text("\n".join(yolo_lines), encoding="utf-8")

    # Write data.yaml
    names_list = ", ".join(repr(n) for n in classes_sorted)
    # Use absolute paths to avoid YOLO resolving from CWD
    abs_root = out_root.resolve()
    train_path = (abs_root / "images" / "train").as_posix()
    val_path = (abs_root / "images" / "val").as_posix()
    test_path = (abs_root / "images" / "test").as_posix()
    data_yaml = "\n".join([
        f"path: {abs_root.as_posix()}",
        f"train: {train_path}",
        f"val: {val_path}",
        f"test: {test_path}",
        f"nc: {len(classes_sorted)}",
        f"names: [{names_list}]",
        "",
    ])
    (out_root / "data.yaml").write_text(data_yaml, encoding="utf-8")

    # Write classes for reference
    (out_root / "classes.txt").write_text("\n".join(classes_sorted), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Convert Supervisely polygons to YOLOv8 detection format.")
    parser.add_argument(
        "--source",
        type=str,
        default="data/datasets/archive",
        help="Root folder containing the dataset archive (e.g., 'archive/Car damages dataset').",
    )
    parser.add_argument(
        "--dataset",
        type=str,
        required=True,
        help="Dataset folder name under --source (e.g., 'Car damages dataset').",
    )
    parser.add_argument(
        "--out",
        type=str,
        default="data/datasets/processed",
        help="Output root for YOLOv8 dataset.",
    )
    parser.add_argument(
        "--split",
        type=str,
        default="0.7,0.2,0.1",
        help="Train,Val,Test split ratios (sum must be 1.0).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for shuffling/splitting.",
    )
    args = parser.parse_args()

    src_root = Path(args.source)
    out_root = Path(args.out)
    split_parts = [float(x) for x in args.split.split(",")]
    if len(split_parts) != 3:
        raise ValueError("--split must have three comma-separated floats")
    split_tuple = (split_parts[0], split_parts[1], split_parts[2])

    target_out = out_root / "yolov8_detection"
    convert_dataset(src_root, target_out, args.dataset, split_tuple, args.seed)
    print(f"[OK] YOLOv8 detection dataset created at: {target_out}")
    print(f"     data.yaml: {target_out / 'data.yaml'}")
    print(f"     classes: {target_out / 'classes.txt'}")


if __name__ == "__main__":
    main()


