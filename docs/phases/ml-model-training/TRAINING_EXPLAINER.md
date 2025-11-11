ML Training Explainer: From Raw Dataset to Trained YOLOv8 Model
===============================================================

Audience
--------
Someone new to computer vision training who wants a complete, plain‑English walkthrough of what we did, why, and how to repeat it.

Scope
-----
- What dataset format we received and why we converted it
- How we converted to YOLOv8 detection format
- How YOLOv8 training works (step-by-step)
- What all the training metrics/terms mean (epoch, mAP, losses, etc.)
- What commands we ran and what the outputs mean
- Where your artifacts (weights, reports, visual predictions) live
- How to sanity‑check your model visually

---

1) Dataset: What we received vs. what YOLOv8 needs
--------------------------------------------------

What we had
- You uploaded a Supervisely-style dataset under `data/datasets/archive/` with folders like `File1/img`, `File1/ann`, and `masks_*`.
- Each image has an annotation JSON in `ann/` containing polygon annotations with a `classTitle` (e.g., "Front-door") and a list of polygon points.

Why convert?
- YOLOv8 detection expects bounding boxes (x, y, width, height) in a specific text format per image, not polygons.
- We chose object detection (bounding boxes) over segmentation (masks) to move faster for MVP—detection trains faster and is easier to integrate.

Result we need for YOLOv8 detection
- Directory structure:
  - `images/{train,val,test}` with JPG/PNG images
  - `labels/{train,val,test}` with matching `.txt` files
  - `data.yaml` describing paths, class names, and counts
- Label format per line: `class_id x_center y_center width height`, all normalized to [0,1] by image size.

---

2) Conversion: How polygons became detection labels
---------------------------------------------------

Script location
- `tools/datasets/convert_supervisely_to_yolov8_detection.py`

What it does
- Reads each JSON in `ann/`, collects polygon points, and converts each polygon to a tight bounding box (min/max of points).
- Normalizes the bounding box to YOLOv8 format (center‑x, center‑y, width, height) divided by image width/height.
- Assigns class IDs (0..N-1) based on alphabetical order of class names; writes `classes.txt` and the `names:` list in `data.yaml`.
- Shuffles and splits items into train/val/test (default 70/20/10).
- Writes absolute paths into `data.yaml` to avoid path resolution issues.

How we ran it
```bash
python tools/datasets/convert_supervisely_to_yolov8_detection.py --dataset "Car damages dataset"
```

Where the converted dataset lives
- `data/datasets/processed/yolov8_detection/`
  - `images/train`, `images/val`, `images/test`
  - `labels/train`, `labels/val`, `labels/test`
  - `data.yaml` (absolute paths)
  - `classes.txt` (class names, one per line)

---

3) YOLOv8: What it is and what it needs
---------------------------------------

YOLOv8 basics
- A family of real‑time object detectors by Ultralytics.
- We used the smallest variant, YOLOv8n (nano), to train quickly and still get solid results.

Environment
- Python virtual environment with GPU-accelerated PyTorch.
- Ultralyics package installed for the `yolo` CLI and Python API.

Key inputs
- Pretrained model checkpoint to start from (`yolov8n.pt`). This is transfer learning—starting from a good general “vision base” and adapting to our car parts.
- Dataset manifest (`data.yaml`) that tells YOLO where images/labels are and what the classes are.

---

4) Training: Commands and what happened
---------------------------------------

Initial fast run (50 epochs)
```bash
yolo detect train \
  model=yolov8n.pt \
  data=data/datasets/processed/yolov8_detection/data.yaml \
  imgsz=640 epochs=50 batch=24 workers=8 device=0 \
  project=runs/yolov8_det name=car-damage-v12
```

Extended run to 150 epochs (started from the best weights we got above)
```bash
yolo detect train \
  model=runs/yolov8_det/car-damage-v12/weights/best.pt \
  data=data/datasets/processed/yolov8_detection/data.yaml \
  imgsz=640 epochs=150 batch=24 workers=8 device=0 \
  project=runs/yolov8_det name=car-damage-v13 patience=50
```

Why two runs?
- First, a quick 50-epoch pass to confirm the pipeline works and see fast results.
- Then, continue training from the best checkpoint to improve performance with little extra time (early stopping enabled by `patience`).

Outputs location
- `runs/yolov8_det/car-damage-v12/` (first run)
- `runs/yolov8_det/car-damage-v13/` (extended run)
  - `weights/best.pt` and `weights/last.pt`
  - `results.csv` and `results.png` (training curves)
  - Confusion matrix images and sample training/validation batches

---

5) Reading the terminal logs and metrics
----------------------------------------

Common terms you saw
- Epoch: One full pass over the entire training set. 50 epochs = the model saw the whole dataset 50 times.
- Batch size: Number of images processed together before a gradient update. We used 24 (tune by VRAM).
- GPU mem: How much GPU memory is used while training. It’s normal to see it close to VRAM limits for efficiency.
- Losses (train/*): Lower is better. They measure how “wrong” the model is during training.
  - box_loss: How well the predicted boxes align with ground truth (localization).
  - cls_loss: How well class labels are predicted (classification).
  - dfl_loss: “Distribution Focal Loss” — helps model learn precise box boundaries.
- Validation metrics (metrics/*): Measured on the validation split (data the model didn’t see during weight updates).
  - precision (P): Of the boxes the model predicted, what fraction are correct? High P = few false positives.
  - recall (R): Of the boxes that should be predicted, what fraction did the model find? High R = few misses.
  - mAP50: Mean Average Precision at IoU=0.5. Think of it as an overall detection score (higher is better).
  - mAP50-95: Same as mAP, averaged across IoU thresholds from 0.5 to 0.95 (stricter, more realistic quality measure).

What “best.pt” means
- During training, YOLO keeps track of the best validation performance and saves the weights that achieved it as `best.pt`.
- This is the checkpoint you should deploy/integrate.

Our results (summaries)
- 50 epochs (car-damage-v12, best.pt on val):
  - Precision ≈ 0.873, Recall ≈ 0.822, mAP50 ≈ 0.873, mAP50-95 ≈ 0.642
- 150 epochs (car-damage-v13, best.pt on val):
  - Precision ≈ 0.887, Recall ≈ 0.846, mAP50 ≈ 0.883, mAP50-95 ≈ 0.644

Interpretation
- The extended run gave a small, consistent bump. Numbers are strong for a YOLOv8n model and suitable for MVP.

---

6) Visual sanity check (why and how)
------------------------------------

Why do this?
- Numbers are great, but the human eye convinces quickly. We want to see boxes landing on the right car parts.

Command we ran
```bash
yolo detect predict \
  model=runs/yolov8_det/car-damage-v13/weights/best.pt \
  source=data/datasets/processed/yolov8_detection/images/val \
  save=True device=0
```

What you get
- Images saved to `runs/detect/predict/` with colored boxes and labels drawn for each detection.
- Open a handful and confirm the detections look reasonable—this matched your observation: “better than I thought.”

---

7) What we achieved and what’s next
-----------------------------------

Accomplished
- Converted a polygon‑annotated dataset into YOLOv8 detection format.
- Trained and validated a YOLOv8n model with strong metrics on your RTX 4070 Ti.
- Verified quality both numerically (mAP, P/R) and visually (predictions on validation images).

Next steps (options)
- Integration: Load `best.pt` in the FastAPI service so `/infer` uses the trained model instead of mock results.
- Polishing (optional): Try `yolov8s.pt` (small model) for higher accuracy, tune epochs/batch/augs, or refine the class set.
- Data improvements (optional): Add more challenging images or rebalance classes if certain parts underperform.

---

Appendix A: Repro Quickstart
----------------------------

Environment (Windows PowerShell from project root)
```bash
python -m venv .venv
. .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install ultralytics pillow opencv-python
python -c "import torch; print('CUDA:', torch.cuda.is_available()); print('Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"
```

Convert dataset
```bash
python tools/datasets/convert_supervisely_to_yolov8_detection.py --dataset "Car damages dataset"
```

Train (fast 50 epochs)
```bash
yolo detect train model=yolov8n.pt data=data/datasets/processed/yolov8_detection/data.yaml imgsz=640 epochs=50 batch=24 workers=8 device=0 project=runs/yolov8_det name=car-damage-v12
```

Continue training (to 150 epochs from best.pt)
```bash
yolo detect train model=runs/yolov8_det/car-damage-v12/weights/best.pt data=data/datasets/processed/yolov8_detection/data.yaml imgsz=640 epochs=150 batch=24 workers=8 device=0 project=runs/yolov8_det name=car-damage-v13 patience=50
```

Validate and visualize
```bash
yolo detect val model=runs/yolov8_det/car-damage-v13/weights/best.pt data=data/datasets/processed/yolov8_detection/data.yaml device=0
yolo detect predict model=runs/yolov8_det/car-damage-v13/weights/best.pt source=data/datasets/processed/yolov8_detection/images/val save=True device=0
```

---

Appendix B: Metric Glossary (quick)
-----------------------------------
- Epoch: One complete pass over the training set.
- Batch size: Number of images processed at once.
- box_loss: How well box coordinates match ground truth.
- cls_loss: How well class predictions match ground truth.
- dfl_loss: Helps precise box boundary learning.
- Precision (P): Of predicted boxes, fraction that are correct.
- Recall (R): Of ground‑truth boxes, fraction that were found.
- mAP50: Overall accuracy at IoU 0.5.
- mAP50-95: Average accuracy over IoU thresholds [0.5..0.95].
- best.pt: Weights from the epoch with best validation performance.


