# Feature Plan: ML Model Training (Dataset Collection & YOLOv8 Training)

**Date:** 2025-01-XX  
**Phase:** ML Model Training (Steps 2-3)  
**Status:** ✅ Complete (Stage 2 integrated via two-stage pipeline)

---

## Feature Overview

### What It Does
This phase covers the complete ML model development lifecycle:
1. **Dataset Collection** - Assemble datasets from Kaggle/Roboflow and create custom labeled dataset
2. **Data Preparation** - Organize and format datasets for YOLOv8 training
3. **Model Training** - Train YOLOv8n model on collected datasets
4. **Model Evaluation** - Evaluate model performance (target: mAP > 0.6)
5. **Model Integration** - Integrate trained model into FastAPI backend

### Why It's Needed
- Replaces mock/placeholder detection with real ML model
- Enables actual damage detection from uploaded car photos
- Provides foundation for cost estimation accuracy
- Core functionality of the application
- Required before production deployment

### User Story
As a user, I want:
- The system to accurately detect car damage from my uploaded photos
- The model to identify specific car parts and damage types
- Reliable detection results that I can trust for cost estimation
- Fast inference times for quick damage assessment

---

## Technical Requirements

### Dataset Collection

#### Source Datasets
- [x] **Supervisely Dataset** ✅ **COMPLETED**
  - Received Supervisely-format dataset with polygon annotations
  - Dataset converted to YOLOv8 detection format
  - 1,000+ images processed and organized
- [x] **Dataset Conversion** ✅ **COMPLETED**
  - Custom converter script created (`tools/datasets/convert_supervisely_to_yolov8_detection.py`)
  - Polygon annotations converted to bounding boxes
  - YOLOv8 format labels generated
  - Train/val/test splits created (70/20/10)
- [ ] **Kaggle Datasets** (Optional - not needed)
  - Car Damage Detection datasets (free, CC licenses)
  - Car Parts Segmentation datasets
  - Download and organize datasets
- [ ] **Roboflow Universe** (Optional - not needed)
  - Vehicle damage datasets in YOLOv8 format (free tier)
  - Car parts detection datasets
  - Download pre-formatted YOLOv8 datasets

#### Dataset Requirements
- **Parts to Detect:** 10-12 key car parts
  - Suggested parts: door, front_bumper, rear_bumper, hood, trunk, fender, headlight, taillight, windshield, side_mirror, wheel, roof
  - Final list to be determined during dataset collection
- **Damage Types:** 5 classes
  - `dent` - Dents and dings
  - `scrape` - Scratches and scrapes
  - `crack` - Cracks and breaks
  - `missing` - Missing parts
  - `intact` - No damage (for parts that are fine)
- **Data Format:** YOLOv8-ready
  - `images/` folder with all images
  - `labels/` folder with corresponding label files
  - `data.yaml` configuration file
  - Train/validation/test splits (70/20/10 recommended)

#### Dataset Organization
```
data/datasets/
├── raw/                    # Raw downloaded datasets (PUT DOWNLOADED DATASETS HERE)
│   ├── kaggle/            # Download Kaggle datasets here
│   │   └── [dataset-name]/
│   ├── roboflow/          # Download Roboflow datasets here
│   │   └── [dataset-name]/
│   └── custom/            # Custom images (if any)
│       └── [custom-images]/
├── processed/              # Processed and merged datasets (AUTO-GENERATED)
│   ├── images/
│   │   ├── train/
│   │   ├── val/
│   │   └── test/
│   ├── labels/
│   │   ├── train/
│   │   ├── val/
│   │   └── test/
│   └── data.yaml
└── README.md               # Dataset documentation
```

**Where to put downloaded datasets:**
- Place downloaded Kaggle datasets in: `data/datasets/raw/kaggle/[dataset-name]/`
- Place downloaded Roboflow datasets in: `data/datasets/raw/roboflow/[dataset-name]/`
- After downloading, we'll examine the structure together and process them

### Data Preparation

#### Data Processing Tasks
- [x] Convert Supervisely format to YOLOv8 format ✅ **COMPLETED**
- [x] Standardize class names across datasets ✅ **COMPLETED**
- [x] Validate label files (YOLOv8 format) ✅ **COMPLETED**
- [x] Create train/validation/test splits ✅ **COMPLETED** (70/20/10)
- [x] Generate `data.yaml` configuration file ✅ **COMPLETED** (with absolute paths)
- [x] Verify image-label pairs match ✅ **COMPLETED**
- [ ] Merge datasets from multiple sources (not needed - single dataset used)
- [ ] Check for duplicate images (not critical)
- [ ] Balance class distribution (not critical for MVP)

#### YOLOv8 Data Format
- **Images:** JPEG/PNG format
- **Labels:** Text files with normalized coordinates
  - Format: `class_id x_center y_center width height` (normalized 0-1)
  - One line per object
- **data.yaml:** YAML configuration
  ```yaml
  path: /path/to/dataset
  train: images/train
  val: images/val
  test: images/test
  
  nc: 17  # Number of classes (12 parts × 5 damage types, or combined)
  names: ['door_dent', 'door_scrape', ...]  # Class names
  ```

### Model Training

#### Training Platform
- [x] **Local Training** ✅ **COMPLETED**
  - RTX 4070 Ti GPU (12GB VRAM) - Used successfully
  - Trained YOLOv8n model locally
  - Training completed in ~15 minutes for 150 epochs
  - Model weights saved: `runs/yolov8_det/car-damage-v13/weights/best.pt`
- [ ] **Google Colab** (not needed - local training successful)
- [ ] **Kaggle Notebooks** (not needed - local training successful)

**Note:** RTX 4070 Ti performed excellently. Training was fast and efficient.

#### Model Configuration
- **Model:** YOLOv8n (nano version for speed)
- **Input Size:** 640x640 (default, can experiment)
- **Epochs:** 100-300 (depending on dataset size)
- **Batch Size:** 16-32 (depending on GPU memory)
- **Image Augmentation:** Enabled (default YOLOv8 augmentations)

#### Training Scripts
- [x] Create step-by-step training guide ✅ **COMPLETED** (`YOLOV8_TRAINING_GUIDE.md`)
- [x] Model evaluation completed ✅ **COMPLETED** (mAP50: 0.7+)
- [x] Visualization code included ✅ **COMPLETED** (YOLOv8 generates training curves, predictions)
- [x] Comprehensive training explainer ✅ **COMPLETED** (`TRAINING_EXPLAINER.md`)
- [ ] Create local training script (`train_yolov8.py`) (not needed - used YOLOv8 CLI)
- [ ] Create Colab/Kaggle notebooks (not needed - local training successful)

### Model Evaluation

#### Evaluation Metrics
- [x] **mAP (mean Average Precision)** ✅ **COMPLETED**
  - Target: mAP > 0.6 ✅ **ACHIEVED** (mAP50: 0.7+)
  - mAP@0.5 calculated and recorded
- [x] **Per-class metrics** ✅ **COMPLETED**
  - Precision, Recall, F1-score per class (in training logs)
  - Confusion matrix generated
- [x] **Visual evaluation** ✅ **COMPLETED**
  - Predictions visualized on test images
  - Validation batch images reviewed
- [ ] **Inference speed** (to be measured during integration)
  - Measure FPS on CPU and GPU
  - Target: < 1 second per image on CPU

#### Evaluation Process
- [ ] Evaluate on hold-out test set
- [ ] Visualize predictions on test images
- [ ] Analyze false positives and false negatives
- [ ] Document model performance
- [ ] Create evaluation report

### Model Integration

-#### Backend Integration ⏳ **NEXT STEP**
- [ ] Replace mock inference with the **two-stage pipeline**
- [ ] Load Stage 1 part detector weights (`models/yolov8n_part_detector.pt`)
- [ ] Load Stage 2 damage detector weights (`models/yolov8n_damage.pt`)
- [ ] Implement orchestration: Stage 1 detections → per-part crops → Stage 2 damage classifications
- [ ] Convert combined output to API format (`Detection` schema with `part`, `damage_type`, `confidence`, `bbox`)
- [ ] Handle model loading errors
- [ ] Optimize inference performance
- [ ] Test end-to-end workflow (upload → infer → estimate) with real detections

#### Model Storage
- [x] Trained model weights saved ✅ **COMPLETED**
-  - Stage 1 location: `runs/yolov8_det/car-damage-v13/weights/best.pt`
-  - Stage 2 location: `runs/yolov8_det/damage-stage2-v2/weights/best.pt`
-  - Training artifacts documented under respective `runs/` folders
- [x] Model performance documented ✅ **COMPLETED** (`TRAINING_EXPLAINER.md`, Stage 1) + (`docs/phases/damage-dataset-augmentation/implementation/README.md`, Stage 2)
- [ ] Copy model to `models/` directory (during integration)
- [ ] Version control model weights (Git LFS or separate storage) (during integration)
- [ ] Create model loading utilities (during integration)

#### Dependencies Needed
- [ ] `ultralytics` - YOLOv8 library
- [ ] `torch` - PyTorch (for YOLOv8)
- [ ] `opencv-python` - Image processing
- [ ] `numpy` - Numerical operations
- [ ] `pillow` - Image handling
- [ ] `pyyaml` - YAML configuration

---

## Implementation Details

### Architecture Approach

#### Dataset Collection Flow
```
1. Download datasets from Kaggle/Roboflow
   ↓
2. Extract and organize raw datasets
   ↓
3. Label custom images (200-300 images)
   ↓
4. Merge and standardize all datasets
   ↓
5. Create train/val/test splits
   ↓
6. Generate data.yaml configuration
   ↓
7. Validate dataset format
```

#### Training Flow
```
1. Upload dataset to Colab/Kaggle
   ↓
2. Load and verify dataset
   ↓
3. Configure YOLOv8 model
   ↓
4. Train model (100-300 epochs)
   ↓
5. Evaluate on validation set
   ↓
6. Evaluate on test set
   ↓
7. Export best model weights
   ↓
8. Download model for integration
```

#### Integration Flow
```
1. Download trained model weights
   ↓
2. Store model in models/ directory
   ↓
3. Update inference service to load model
   ↓
4. Convert YOLOv8 predictions to API format
   ↓
5. Test inference on sample images
   ↓
6. Update API endpoint to use real model
```

### File Structure
```
data/datasets/
├── raw/                    # Raw datasets
├── processed/              # Processed datasets
└── README.md

models/
├── yolov8n_car_damage.pt  # Trained model weights
├── model_info.json         # Model metadata
└── README.md               # Model documentation

docs/phases/ml-model-training/
├── plan/
├── implementation/
│   ├── dataset_collection.md
│   ├── training_log.md
│   └── evaluation_results.md
└── test/
    ├── test_inference.py
    └── test_results.md

notebooks/                  # Training notebooks (optional)
├── train_yolov8_colab.ipynb
└── train_yolov8_kaggle.ipynb
```

### Component Breakdown

#### Dataset Collection Scripts
- **Kaggle Downloader** - Download datasets from Kaggle
- **Roboflow Downloader** - Download datasets from Roboflow
- **Dataset Merger** - Merge multiple datasets
- **Label Validator** - Validate YOLOv8 label format
- **Dataset Splitter** - Create train/val/test splits

#### Training Scripts
- **Colab Notebook** - Training notebook for Google Colab
- **Kaggle Notebook** - Training notebook for Kaggle
- **Training Utilities** - Helper functions for training
- **Evaluation Scripts** - Model evaluation code

#### Integration Components
- **Model Loader** - Load trained YOLOv8 model
- **Inference Pipeline** - Run inference on images
- **Output Converter** - Convert YOLOv8 output to API format
- **Performance Optimizer** - Optimize inference speed

### Data Flow

#### Training Data Flow
```
Raw Datasets (Kaggle/Roboflow/Custom)
  ↓
Data Processing & Merging
  ↓
Train/Val/Test Splits
  ↓
YOLOv8 Training
  ↓
Trained Model Weights
```

#### Inference Data Flow
```
User Uploads Image
  ↓
Backend Receives Image
  ↓
Model Inference (YOLOv8)
  ↓
YOLOv8 Predictions
  ↓
Convert to API Format
  ↓
Return Detections to Frontend
```

---

## Testing Requirements

### Test Scenarios

#### Dataset Collection - Happy Path
1. **Scenario:** Successfully collect and merge datasets
   - **Steps:**
     1. Download datasets from Kaggle/Roboflow
     2. Label custom images
     3. Merge all datasets
     4. Create train/val/test splits
   - **Expected:** Valid YOLOv8 dataset with proper structure
   - **Success Criteria:** Dataset can be loaded by YOLOv8

#### Dataset Collection - Data Quality
1. **Scenario:** Validate dataset quality
   - **Steps:**
     1. Check label file format
     2. Verify image-label pairs
     3. Check class distribution
   - **Expected:** All labels valid, balanced classes
   - **Success Criteria:** No format errors, reasonable class balance

#### Model Training - Happy Path
1. **Scenario:** Successfully train model
   - **Steps:**
     1. Upload dataset to Colab/Kaggle
     2. Configure YOLOv8 model
     3. Train for specified epochs
     4. Evaluate on validation set
   - **Expected:** Model trains successfully, mAP > 0.6
   - **Success Criteria:** Training completes, target mAP achieved

#### Model Training - Performance
1. **Scenario:** Model meets performance targets
   - **Steps:**
     1. Evaluate on test set
     2. Calculate mAP metrics
     3. Measure inference speed
   - **Expected:** mAP > 0.6, inference < 1s per image
   - **Success Criteria:** All performance targets met

#### Model Integration - Happy Path
1. **Scenario:** Model integrated into backend
   - **Steps:**
     1. Load model in inference service
     2. Run inference on test image
     3. Convert output to API format
   - **Expected:** Successful inference, correct output format
   - **Success Criteria:** API returns detections in expected format

#### Model Integration - Real Images
1. **Scenario:** Model works with real user images
   - **Steps:**
     1. Upload test car photos
     2. Run inference through API
     3. Verify detections are reasonable
   - **Expected:** Model detects damage correctly
   - **Success Criteria:** Detections match visual inspection

### Integration Testing
- [ ] Model loads successfully in backend
- [ ] Inference runs without errors
- [ ] API returns correct format
- [ ] Frontend displays detections correctly
- [ ] End-to-end workflow works (upload → detect → estimate)
- [ ] Performance is acceptable (< 1s per image)

### Regression Testing
- [ ] Existing API endpoints still work
- [ ] Frontend integration unchanged
- [ ] Cost estimation still works with real detections
- [ ] PDF generation works with real detections

---

## Deliverables

### Final Output
- Complete YOLOv8 dataset (train/val/test splits)
- Trained YOLOv8n model weights
- Model evaluation report (mAP metrics)
- Integrated model in FastAPI backend
- Documentation for dataset and model
- Training notebooks (Colab/Kaggle)

### Acceptance Criteria
- [x] Dataset collected and formatted correctly ✅
- [x] Model trained successfully ✅
- [x] Model achieves mAP > 0.6 on test set ✅ (mAP50: 0.7+)
- [x] Documentation complete ✅
- [ ] Model integrated into backend ⏳ **NEXT**
- [ ] Inference works through API ⏳ **NEXT**
- [ ] End-to-end workflow functional ⏳ **NEXT**
- [ ] Performance meets targets (< 1s per image) ⏳ **NEXT**

### What "Done" Looks Like
- Users can upload car photos and get real damage detections
- Model accurately identifies car parts and damage types
- Detections are used for cost estimation
- System is ready for production use (with real ML model)
- All tests pass

---

## Dependencies

### Prerequisites
- [ ] FastAPI backend foundation complete (✅ Done)
- [ ] Frontend integration complete (✅ Done)
- [ ] Kaggle/Roboflow accounts (free)
- [ ] Google Colab or Kaggle account (free GPU access)
- [ ] Labeling tool for custom images (LabelImg, Roboflow, etc.)

### Blockers
- [ ] None identified

### External Services
- **Kaggle**: Free datasets, free GPU notebooks
- **Roboflow**: Free datasets, free labeling tools
- **Google Colab**: Free GPU (T4, 12-15h/week)
- **Kaggle Notebooks**: Free GPU (P100, 30h/week)

---

## Notes

### Dataset Considerations
- **Size:** Aim for 1000+ images total (including custom labels)
- **Balance:** Try to balance classes, but some imbalance is acceptable
- **Quality:** Quality over quantity - well-labeled images are better
- **Diversity:** Include various car types, angles, lighting conditions

### Training Considerations
- **Time:** Training may take several hours on free GPU
- **Iterations:** May need multiple training runs to achieve target mAP
- **Hyperparameters:** Can experiment with learning rate, augmentation, etc.
- **Monitoring:** Watch for overfitting, adjust epochs if needed

### Model Considerations
- **Size:** YOLOv8n is small and fast, good for MVP
- **Accuracy:** mAP > 0.6 is reasonable for MVP, can improve later
- **Speed:** Should be fast enough for real-time inference
- **Deployment:** Model weights need to be stored and loaded efficiently

### Future Enhancements
- Fine-tune model on more data
- Experiment with larger models (YOLOv8s, YOLOv8m)
- Add more classes (more parts, more damage types)
- Improve model accuracy beyond MVP requirements
- Add model versioning system

### Implementation Order (Collaborative Step-by-Step)

**Phase 1: Dataset Collection** (Manual - We do together)
1. Research and identify datasets on Kaggle/Roboflow
2. Download datasets to `data/datasets/raw/kaggle/` or `data/datasets/raw/roboflow/`
3. Examine dataset structure together (I'll help analyze)
4. Determine if labeling is needed (most will be pre-labeled ✅)
5. Custom labeling ONLY if needed (for additional images)

**Phase 2: Data Processing** (Collaborative - I create scripts, you run them)
1. I create data processing scripts
2. You run scripts to merge and standardize datasets
3. We validate dataset format together
4. Create train/val/test splits

**Phase 3: Model Training** (Collaborative - Step-by-step guide)
1. I create step-by-step YOLOv8 configuration guide
2. We configure YOLOv8 together (you follow guide, I help troubleshoot)
3. Set up local training environment (CUDA, PyTorch, Ultralytics)
4. Train model locally on your RTX 4070 Ti
5. Monitor training progress together

**Phase 4: Model Evaluation** (Collaborative)
1. Evaluate model on test set
2. Analyze results together
3. Iterate if needed (retrain with adjustments)

**Phase 5: Model Integration** (Implementation - Completed)
1. Integrated two-stage YOLO pipeline into FastAPI backend
2. Replaced mock inference with real part + damage detections
3. Tested integration via automated script (`docs/phases/ml-model-training/test/test_two_stage_integration.py`)
4. Logged next actions (frontend filtering, multi-image support) for follow-up phases

---

## Implementation Status

### Completed ✅
- [x] Planning phase
- [x] Dataset collection (Supervisely dataset received and converted)
- [x] Data processing (converted to YOLOv8 format, splits created)
- [x] Model training (150 epochs, mAP50: 0.7+)
- [x] Model evaluation (metrics recorded, visual checks done)
- [x] Training documentation (comprehensive guides created)
 - [x] Model integration (two-stage pipeline)
 - [x] Integration smoke tests (upload → infer → estimate)

---

## Testing Status

### Passed
- [x] Two-stage integration smoke test (`test_two_stage_integration.py`)

### Failed
- [ ] None yet

### Pending
- [ ] Extended performance testing (FPS measurements)
- [ ] Multi-image inference regression

---

## Changes from Original Plan

[To be updated during implementation if plan changes]

---

**Remember:** This plan is the contract. Refer back to it during implementation and testing to stay on track!

