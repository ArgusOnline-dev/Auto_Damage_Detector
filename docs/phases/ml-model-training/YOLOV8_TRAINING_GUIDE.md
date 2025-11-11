# YOLOv8 Configuration & Training Guide

**Purpose:** Step-by-step guide for configuring and training YOLOv8 model locally

**Status:** 🟡 To be created during implementation

---

## Overview

This guide will walk you through:
1. Setting up local training environment
2. Configuring YOLOv8 for your dataset
3. Understanding YOLOv8 parameters
4. Training the model
5. Monitoring training progress
6. Evaluating model performance

---

## Prerequisites

- RTX 4070 Ti GPU (12GB VRAM) ✅
- CUDA installed
- Python environment set up
- Dataset ready in YOLOv8 format

---

## Step-by-Step Sections

### 1. Environment Setup
- Install NVIDIA GPU driver (latest Studio or Game Ready)
- Install CUDA Toolkit (matching your PyTorch version; optional if using pip wheels)
- Create/activate a Python virtual environment
- Install PyTorch with CUDA support (per https://pytorch.org/get-started/locally/)
- Install Ultralytics (YOLOv8)
- Verify GPU access in Python

Example (Windows PowerShell):
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install --upgrade pip
# Pick the right command from pytorch.org for CUDA 12.1 or 11.8. Example for CUDA 12.1:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install ultralytics
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

### 2. Dataset Configuration
- Understanding `data.yaml` structure
- Configuring class names
- Setting dataset paths
- Validating dataset format

Converter (Supervisely → YOLOv8 detection):
```bash
python tools/datasets/convert_supervisely_to_yolov8_detection.py --dataset "Car damages dataset"
```
Output will be in `data/datasets/processed/yolov8_detection/` with `data.yaml`.

### 3. Model Configuration
- Choosing YOLOv8 variant (nano/small/medium)
- Understanding hyperparameters
- Configuring training parameters
- Setting up training script

Basic training params (good starting point on RTX 4070 Ti):
- model: yolov8n.pt
- imgsz: 640
- epochs: 100-200
- batch: 16-32 (adjust if OOM)
- workers: 8

### 4. Training Process
- Starting training
- Monitoring training progress
- Understanding training metrics
- Saving checkpoints

Start training (Ultralytics CLI):
```bash
yolo detect train model=yolov8n.pt data=data/datasets/processed/yolov8_detection/data.yaml imgsz=640 epochs=150 batch=24 workers=8 device=0 project=runs/yolov8_det name=car-damage-v1
```

Or Python API:
```python
from ultralytics import YOLO

model = YOLO("yolov8n.pt")
model.train(
    data="data/datasets/processed/yolov8_detection/data.yaml",
    imgsz=640,
    epochs=150,
    batch=24,
    workers=8,
    device=0,
    project="runs/yolov8_det",
    name="car-damage-v1",
)
```

### 5. Evaluation
- Evaluating on validation set
- Evaluating on test set
- Understanding mAP metrics
- Visualizing predictions

Quick eval/inference after training:
```bash
yolo detect val model=runs/yolov8_det/car-damage-v1/weights/best.pt data=data/datasets/processed/yolov8_detection/data.yaml
yolo detect predict model=runs/yolov8_det/car-damage-v1/weights/best.pt source=some_folder_or_image.jpg save=True
```

---

**Note:** This guide will be created step-by-step as we progress through the training phase. Each step will be documented with screenshots/examples to make it easy to follow.

