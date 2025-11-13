# Label Fusion Utilities

Scripts used in the damage dataset augmentation phase:

1. `run_part_inference.py` – Runs the existing part detector over the
   damage dataset images and persists raw detections (`bbox_xyxy`,
   confidence, part label) per image.
2. `match_damage_to_parts.py` – Loads the damage polygons (Supervisely
   JSON) and the part detections, matches them via IoU, normalizes the
   damage label into the 8 standard categories, and writes per-image
   fused annotations describing `part`, `damage_type`, and the normalized
   bounding boxes.
3. `build_damage_dataset.py` – Converts fused annotations into a
   YOLOv8-ready dataset (Stage 2) that contains only the normalized
   damage classes, along with `classes.txt`, `data.yaml`, and stats.
4. `build_combined_dataset.py` – Legacy helper that can still generate
   combined part+damage labels if needed for experiments.

Typical usage:

```bash
# 1) Run part detector on damage dataset
python tools/label_fusion/run_part_inference.py \
  --images-dir data/datasets/archive/Car\\ parts\\ dataset/File1/img \
  --model-path runs/yolov8_det/car-damage-v13/weights/best.pt \
  --output-dir data/datasets/processed/part_detections

# 2) Match damage polygons to detected parts (normalizes damage labels)
python tools/label_fusion/match_damage_to_parts.py \
  --damage-annotations data/datasets/archive/Car\\ parts\\ dataset/File1/ann \
  --damage-images data/datasets/archive/Car\\ parts\\ dataset/File1/img \
  --part-detections data/datasets/processed/part_detections \
  --output-dir data/datasets/processed/part_damage_matches

# 3) Build damage-only YOLO dataset (Stage 2)
python tools/label_fusion/build_damage_dataset.py \
  --matches-dir data/datasets/processed/part_damage_matches \
  --output-root data/datasets/processed/yolov8_damage_only
```

After the dataset is generated, retrain YOLOv8 using the new
`yolov8_damage_only/data.yaml` to obtain the Stage 2 damage model.
