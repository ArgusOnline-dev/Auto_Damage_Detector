# Feature Plan: Damage Dataset Augmentation & Retraining

**Date:** 2025-02-XX  
**Phase:** Damage Dataset Augmentation (Step 3.5)  
**Status:** ✅ Completed (Stage 2 damage model trained)

---

## Feature Overview

### What It Does
Automates the creation of damage labels from the Supervisely dataset and trains a dedicated YOLOv8 model (Stage 2) that predicts **only the normalized damage type (8 classes)** for each detected part. The existing part detector (Stage 1) remains unchanged; inference becomes a two-stage pipeline: part detection → crop → damage classification.

### Why It's Needed
- The combined `part_damage` approach produced >150 sparse classes and low mAP. Splitting the problem into two models lets each network specialize.
- Severity/cost engines still need reliable damage types (dent/scratch/cracked/missing/etc.); predicting them independently of the part keeps the label space small and learnable.
- Automation still saves us from manual relabeling while letting us reuse the high-quality part detector.

### User Story
As a developer, I want an automated pipeline that enriches our dataset with damage labels and retrains YOLOv8 so that the API returns realistic damage classifications without manual labeling.

---

## Technical Requirements

### Backend/ML Changes
- [x] Script to run the trained part detector across the damage dataset (batch inference, JSON output).
- [x] Matching logic to associate each damage polygon with the best-matching detected part (IoU based) and normalize labels.
- [x] Intact-label fallback so unmatched parts become negative samples.
- [x] Damage-only dataset builder with balancing/oversampling plus manifest (`data.yaml`, `classes.txt`, `stats.json`).
- [x] Stage 2 YOLOv8 training on the damage-only dataset (`damage-stage2-v2`) and export of `models/yolov8n_damage.pt`.
- [x] Model evaluation with per-class metrics recorded in `runs/yolov8_det/damage-stage2-v2/`.
- [ ] Update FastAPI inference service to orchestrate Stage 1 + Stage 2 and surface real damage types.

### Frontend Changes
- [ ] None immediately (frontend already consumes `damage_type`; it will receive real values once backend updates).

### Database Changes
- [ ] None.

### API Endpoints
| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| POST | `/api/v1/infer` | Returns real part+dmg detections from new model | Planned (reuse) |

---

## Implementation Details

### Architecture Approach
1. **Part Detector Pass**: Use existing YOLO weights to detect parts in every image of the damage-only dataset; persist detections (bbox, class, confidence) to JSON per image.
2. **Damage Polygon Matching**: For each damage annotation, compute its bbox and match to the overlapping part detection (IoU threshold + confidence gating). Generate combined labels.
3. **Quality Filters**: Drop low-confidence matches, log unmatched polygons for optional review.
4. **Dataset Build**: Write YOLOv8-ready folders (`images`, `labels`, `data.yaml`) with combined class list and statistics (counts, coverage, confidence distributions).
5. **Retrain/Fine-tune**: Run YOLOv8 training initialized from previous `best.pt`, targeting combined classes; log metrics.
6. **Evaluation & Export**: Produce metrics, confusion matrix, visual predictions; copy `best.pt` to `models/` with metadata for integration.

### File Structure
```
tools/label_fusion/
├── run_part_inference.py
├── match_damage_to_parts.py
├── build_damage_dataset.py
└── README.md
data/datasets/processed/yolov8_damage_only/
├── images/{train,val,test}
├── labels/{train,val,test}
├── classes.txt
├── data.yaml
└── stats.json
runs/yolov8_det/damage-stage2-v2/
models/
├── yolov8n_part_detector.pt   # existing Stage 1 weights
└── yolov8n_damage.pt          # new Stage 2 weights
```

### Component Breakdown
- **Stage 1 (unchanged)** `run_part_inference.py`: generates part detections used to crop images or associate damage polygons with the correct part.
- **Stage 2 preprocessing**:
  - `match_damage_to_parts.py`: now normalizes all damage labels into the 8-class set and outputs per-damage annotations (with links to the owning part/crop).
  - `build_damage_dataset.py` *(successor to combined dataset builder)*: produces a YOLOv8-ready dataset with **only damage classes** (`['dent','scratch','cracked','broken_part','missing_part','paint_chip','flaking','corrosion','intact']`). Behind the scenes it can still create part-aware folders for traceability, but the YOLO labels contain only damage IDs.
- **Training**: YOLOv8 damage model (`part-damage-stage2`) trained on the new dataset.
- **Inference orchestration**: service logic loads both models; Stage 1 outputs part boxes, Stage 2 predicts damage class for each box/crop.

### Data Flow
```
Damage dataset images + polygons
    ↓
Part detector predictions (Stage 1)
    ↓
IoU matcher + intact fallback + crop metadata
    ↓
Damage-only YOLO dataset (8 damage + intact classes, balanced)
    ↓
YOLOv8 damage model (Stage 2)
    ↓
FastAPI inference orchestrates Stage 1 + Stage 2 → part + damage_type
```

## Implementation Outcome (2025-02-XX)
- Generated balanced damage dataset (generated locally under `data/datasets/processed/yolov8_damage_only/`, not tracked) with 814 images, 9 classes (including `intact`), and ≥200 samples for each minority damage class via controlled duplication.
- Stage 2 YOLOv8n training (`runs/yolov8_det/damage-stage2-v2/`) achieved **mAP50 0.5895** and **mAP50-95 0.4072** at epoch 148, with key classes (`missing_part`, `broken_part`, `paint_chip`) above 0.7 mAP50.
- Final weights stored at `models/yolov8n_damage.pt`; inference artifacts (confusion matrices, predictions) documented under the run directory.

## Next Steps
1. **Backend integration:** load both Stage 1 and Stage 2 weights inside `apps/api/services/ml` and merge detections so `/infer` returns `part + damage_type`.
2. **End-to-end QA:** run upload → infer → estimate to confirm severity/cost engines consume the new damage types.
3. **Optional refinements:** explore `yolov8s` backbone or stronger augmentations if we need to push mAP50 past the 0.6 target after integration tests.

---

## Testing Requirements

### Test Scenarios

#### Happy Path
1. **Scenario:** Generate combined labels for an image with both part and damage annotations.
   - **Steps:** Run pipeline on sample subset.
   - **Expected Backend:** New label file contains class `part_damage` with normalized bbox; stats report counts it.
   - **Success Criteria:** Bounding box overlaps > threshold and class list updated.
2. **Scenario:** YOLO fine-tune completes with target metrics.
   - **Expected Backend:** `metrics/mAP50` ≥ 0.6 overall; per-class counts logged.

#### Edge Cases
1. **Scenario:** Damage polygon without matching part detection.
   - **Expected:** Entry logged to “unmatched” report; image optionally queued for review.
2. **Scenario:** Multiple damages overlap same part.
   - **Expected:** Highest IoU damage kept per part (configurable); duplicates avoided.

#### Error Handling
1. **Scenario:** Missing inference outputs or corrupted JSON.
   - **Expected:** Pipeline aborts with descriptive message and leaves log entry.

### Integration Testing
- [ ] End-to-end `upload → infer → estimate` returns real `damage_type`.
- [ ] Verify model loader handles new weight path.

### Regression Testing
- [ ] Original part-only detections still reasonable (no catastrophic drop).
- [ ] API responses stay compatible with frontend schema.

---

## Deliverables

### Final Output
- Automated scripts + dataset artifacts.
- YOLOv8 model (`models/yolov8n_part_damage.pt`) with metrics + documentation.
- Updated inference service wired to new model.

### Acceptance Criteria
- [ ] Combined dataset built with ≥80% of damage annotations matched to parts.
- [ ] Model achieves mAP50 ≥ 0.6 overall and ≥0.5 for each critical class (door, bumper, hood).
- [ ] `/api/v1/infer` returns real `damage_type` values for test images.

### What "Done" Looks Like
We can upload a photo through the frontend, receive detections that state both the part and damage category, feed them through severity/cost pipelines, and generate a report without mock data.

---

## Dependencies

### Prerequisites
- [ ] Existing YOLO part detector weights.
- [ ] Damage dataset accessible under `data/datasets/archive/Car parts dataset`.
- [ ] Ultralytics + PyTorch installed (GPU preferred).

### Blockers
- [ ] None identified; optional manual QA time if match rate is low.

---

## Notes
- Keep artifacts small enough or store large intermediates outside git/LFS.
- Matching thresholds (IoU, confidence) should be configurable via `.env` or CLI arguments.
- Consider future extension to support multi-label (multiple damages per part).

---

## Implementation Status

### Completed
- [ ] None

### In Progress
- [ ] Planning

### Pending
- [ ] Pipeline scripts
- [ ] Dataset build
- [ ] Training & evaluation
- [ ] Backend integration

---

## Testing Status

### Passed
- [ ] None

### Failed
- [ ] None

### Pending
- [ ] Pipeline unit tests
- [ ] Training QA
- [ ] API regression tests

---

## Changes from Original Plan

N/A (initial plan).

---

**Remember:** This plan is the contract. Refer back to it during implementation and testing to stay on track!
