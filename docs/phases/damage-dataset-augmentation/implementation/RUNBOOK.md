# Damage Dataset Augmentation Runbook

Use this runbook when executing the label-fusion pipeline for this
phase. It assumes you already read the plan
(`docs/phases/damage-dataset-augmentation/plan/2025-02-XX-damage-dataset-augmentation-v1.0.md`).

## Why This Phase Exists

The current YOLO model only predicts **which car part** is visible
because the training dataset lacked `damage_type` labels. The damage
dataset we received, however, only annotates **damage categories** (dent,
scratch, broken part, etc.) without indicating which part they belong
to. This phase bridges that gap by:

1. Running the existing part detector on the damage dataset to locate
   the parts in each image.
2. Matching those detected parts with the damage polygons to normalize
   each annotation into one of the 8 standard damage classes (dent,
   scratch, cracked, broken_part, missing_part, paint_chip, flaking,
   corrosion).
3. Building a **damage-only YOLOv8 dataset** and training a Stage 2
   damage detector. At inference time we will run Stage 1 (part
   detector) and Stage 2 (damage detector) sequentially, then join the
   results by overlap so every part receives a `damage_type`.

Once finished, the inference API will provide real damage classifications
driven by two specialized models instead of one large, low-accuracy
network.

## Prerequisites

- Windows virtual environment already set up at `.venv` with
  `ultralytics`, `torch`, `tqdm`, etc. (see `requirements.txt`).
- Damage dataset present under
  `data/datasets/archive/Car parts dataset/File1/`.
- Existing part detector weights at
  `runs/yolov8_det/car-damage-v13/weights/best.pt`.
- Enough disk space for intermediate artifacts (detection JSON, fused
  matches, and the new dataset).

> **Tip:** Run the commands from **Windows PowerShell or CMD** so the
> `.venv\Scripts\python.exe` interpreter (with GPU support) is used. The
> WSL shell currently lacks pip/ultralytics, so the scripts will fail
> there.

## Commands To Run

From the repository root (`Auto_Damage_Detector`):

```powershell
# 0) Activate virtual environment (PowerShell)
.\.venv\Scripts\Activate.ps1

# 1) Run existing part detector on damage dataset images
python tools\label_fusion\run_part_inference.py `
  --images-dir "data/datasets/archive/Car parts dataset/File1/img" `
  --model-path runs/yolov8_det/car-damage-v13/weights/best.pt `
  --output-dir data/datasets/processed/part_detections `
  --device 0 `
  --confidence-thresh 0.4

# 2) Match damage polygons to detected parts (tight thresholds + normalization)
python tools\label_fusion\match_damage_to_parts.py `
  --damage-annotations "data/datasets/archive/Car parts dataset/File1/ann" `
  --damage-images "data/datasets/archive/Car parts dataset/File1/img" `
  --part-detections data/datasets/processed/part_detections `
  --output-dir data/datasets/processed/part_damage_matches `
  --iou-threshold 0.10 `
  --min-part-confidence 0.5 `
  --fallback-min-iou 0.05

# 3) Build damage-only YOLOv8 dataset (Stage 2 input)
python tools\label_fusion\build_damage_dataset.py `
  --matches-dir data/datasets/processed/part_damage_matches `
  --output-root data/datasets/processed/yolov8_damage_only `
  --train-ratio 0.7 `
  --val-ratio 0.2 `
  --min-damages-per-image 1
```

After step 3, verify that `data/datasets/processed/yolov8_damage_only`
contains `images/`, `labels/`, `classes.txt`, `data.yaml`, and
`stats.json`. The `stats.json` file records:
- Class distribution across the 8 damage categories
- Total images

Check `stats.json` to confirm:
- Each damage class has sufficient coverage (ideally dozens of samples)
- The total number of images roughly matches expectations (≈800)

## Next Steps After Running Commands

1. **Train the Stage 2 YOLOv8 damage model** using the new dataset:
   ```bash
   yolo detect train \
     model=yolov8n.pt \
     data=data/datasets/processed/yolov8_damage_only/data.yaml \
     imgsz=640 epochs=150 batch=24 device=0 \
     project=runs/yolov8_det name=damage-stage2-v1
   ```
2. Record metrics, sample predictions, and copy the new `best.pt` into
   `models/yolov8n_damage.pt`.
3. Update the FastAPI inference service to load **both** models:
   - Stage 1 YOLO (`yolov8n_part_detector.pt`) to detect parts.
   - Stage 2 YOLO (`yolov8n_damage.pt`) to detect damage types.
   Merge detections by overlapping boxes so each part receives a
   `damage_type`.

## Troubleshooting

- **tqdm/ultralytics not found:** make sure you’re running inside the
  `.venv` and that `pip install -r requirements.txt` has been executed
  (from Windows PowerShell where pip is available).
- **“No part detections found” for an image:** lower
  `--confidence-thresh` in `run_part_inference.py` or rerun with
  `--max-images` for testing.
- **Low IoU matches:** adjust `--iou-threshold` / `--fallback-min-iou`
  in `match_damage_to_parts.py` and inspect the JSON logs for unmatched
  entries.
- **Disk usage:** the intermediate directories can be safely removed
  (`part_detections`, `part_damage_matches`,
  `yolov8_damage_only`) once artifacts are validated and backed up.

Keep this runbook in sync with any script changes so future sessions can
execute the phase without re-reading the entire codebase.
