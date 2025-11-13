# ML Model Training Phase - Test Documentation

This folder contains test documentation and results for the ML Model Training phase.

## Overview

This phase covers testing of:
1. Dataset collection and validation
2. Model training and evaluation
3. Model integration into backend
4. End-to-end inference testing

## Test Run: Two-Stage Model Integration (2025-02-XX)

Use this checklist whenever we validate the two-stage inference pipeline (Stage 1 part detector + Stage 2 damage detector) and its downstream effects.

### Prerequisites
- `models/yolov8n_part_damage.pt` (Stage 1) and `models/yolov8n_damage.pt` (Stage 2) exist locally or paths overridden via `.env` (`PART_MODEL_PATH`, `DAMAGE_MODEL_PATH`).
- Required packages installed in the venv (`ultralytics`, `torch`, etc.).
- Backend running locally (`uvicorn apps.api.main:app --reload`).

### Test Steps
1. **Upload sample image**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/upload" \
        -F "files=@<path-to-sample-image>.jpg"
   ```
   - **Verify:** Response contains `file_ids` array. Note the first ID for reuse.

2. **Run inference**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/infer" \
        -H "Content-Type: application/json" \
        -d '{"file_ids": ["<file-id-from-upload>"]}'
   ```
   - **Verify:** Response includes real detections with both `part` and `damage_type`. Parts with no damage should show `damage_type: "intact"`. Check confidence scores are reasonable (>0.25) and bounding boxes look plausible.

3. **Estimate costs (optional but recommended)**
   - Take the `detections` array from `/infer`, plug into `/estimate`:
     ```bash
     curl -X POST "http://localhost:8000/api/v1/estimate" \
          -H "Content-Type: application/json" \
          -d '{
                "detections": [...],
                "labor_rate": 150,
                "use_oem_parts": true
              }'
     ```
   - **Verify:** API returns populated `line_items` and `totals`. Spot-check severity/cost outputs for obvious errors.

4. **Frontend smoke test (if applicable)**
   - Start the React app, upload the same image, ensure detections and cost tables match API tests.

### Expected Results
- `/upload` succeeds with HTTP 200 and returns at least one file ID.
- `/infer` returns ≥1 detection with real damage types (no placeholders).
- `/estimate` produces cost line items without server errors.
- Backend logs show no model load errors or stack traces.

### Automated Test Script

An automated test script is available at the project root: `test_two_stage_integration.py`

**Usage:**
```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
# or
source .venv/bin/activate      # Linux/Mac

# Ensure backend is running
uvicorn apps.api.main:app --reload

# Run tests (in a separate terminal)
python test_two_stage_integration.py
```

The script automatically:
1. Checks backend health
2. Uploads multiple sample images from the training dataset
3. Runs `/infer` twice (with/without intact filtering) and verifies payload structure
4. Tests cost estimation endpoint using filtered detections
5. Reports pass/fail status for each step

**Test Results:**
- **Date:** 2025-02-XX
- **Status:** ✅ All tests passed
- **Script Location:** `Auto_Damage_Detector/test_two_stage_integration.py`

**Latest Test Run (Backend Integration Polish Phase):**
```
[1/5] Checking backend health... ✅ PASS
[2/5] Uploading sample images... ✅ PASS
  - Uploaded `data/samples/images/Car damages 102.jpg`
  - Uploaded `data/samples/images/Car damages 201.jpg`
[3/5] Running inference with intact parts... ✅ PASS
  - Image 1: 19 detections (all intact)
  - Image 2: 18 detections (all intact)
  - filtered_count=0
[3/5] Running inference without intact parts... ✅ PASS
  - Image 1: 2 detections (damaged parts only)
  - Image 2: 0 detections (all were intact, filtered out)
  - filtered_count=35 (35 intact detections filtered across both images)
[4/5] Testing cost estimation... ✅ PASS
  - Line items: 2
  - Totals: min=$2,900 likely=$4,900 max=$5,880
```

**Key Features Validated:**
- ✅ Multi-image upload and processing
- ✅ `include_intact` filtering works correctly
- ✅ `filtered_count` accurately tracks removed detections
- ✅ Empty detection lists handled gracefully
- ✅ Two-stage model pipeline (Stage 1: parts, Stage 2: damage) working correctly

**Issues Fixed:**
- Updated `run.py` to use `python -m uvicorn` instead of direct `uvicorn` command
- Installed missing dependencies (FastAPI, uvicorn, etc.) in virtual environment
- Fixed `FileNotFoundError` import in `inference.py` to use custom exception class
- Updated test script image paths to use the lightweight fixtures under `data/samples/images/`

### Status
**Current Status:** 🟢 Automated test script ready. Run `python test_two_stage_integration.py` after starting the backend. Document actual run logs/results here after each test session.
