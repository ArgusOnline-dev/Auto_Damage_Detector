# Feature Plan: Backend Integration Polish (Stage 1 + Stage 2 + API UX)

**Date:** 2025-02-XX  
**Phase:** Backend Integration Polish (Step 4/5 follow-up)  
**Status:** ✅ Completed

---

## Feature Overview

### What It Does
Hardens the FastAPI backend around the new two-stage ML pipeline so real detections flow cleanly into the API and UI. Scope includes filtering/aggregation logic, multi-image handling, inference performance checks, and regression tests that keep `/upload → /infer → /estimate` stable.

### Why It's Needed
- The ML phase delivered a functioning two-stage detector, but the API still behaves like the placeholder version (single-image support, noisy “intact” rows, no performance telemetry).
- Frontend/UX issues (e.g., too many intact rows, messy overlays) originate from backend payloads not being curated.
- Before we proceed to VIN/GPT and demo prep, `/infer` needs to be production-ready.

### User Story
As a developer/QA engineer, I want `/infer` and `/estimate` to return clean, reliable payloads so the React UI, severity/cost logic, and future integrations can trust the backend without manual cleanup.

---

## Technical Requirements

### Backend Changes (Completed)
- [x] Support multiple file IDs in `run_inference`, returning per-image results.
- [x] Optional `include_intact` flag and response metadata (`filtered_count`).
- [x] Standardized payload for detections (snake_case labels, `[x1,y1,x2,y2]` boxes).
- [x] Added latency logging per image.
- [x] Added structured error propagation via custom exceptions.

### Frontend/UX Alignment
- [x] Documented API response in test README so frontend can filter `intact` detections.

### Testing/Tooling
- [x] Extended `test_two_stage_integration.py` for multi-image + filtering.
- [ ] (Optional) Load-test script for latency tracking (deferred).

### API Endpoints
| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| POST | `/api/v1/infer` | Returns curated detection payloads for multiple images | Planned update |
| POST | `/api/v1/estimate` | Consumes curated detections (no change) | Regression |

---

## Implementation Details

### Architecture Approach
1. **Payload refactor:** adjust `apps/api/services/ml/inference.py` to return a list of per-image detections plus metadata (`model_version`, `latency_ms`, etc.).
2. **Filtering hooks:** allow config or query parameters (e.g., `?include_intact=false`) to trim out undamaged parts so the frontend can request only what it needs.
3. **Performance logging:** wrap Stage 1/Stage 2 calls with timers and log to the existing logger; optionally surface aggregated metrics in `/health`.
4. **Error handling:** wrap YOLO calls in try/except to convert `ModelNotFoundError`, `CUDAError`, etc., into 4xx/5xx responses.
5. **Testing:** update the existing test script + docs to cover new payload structure and filtering toggles.

### File Structure
```
apps/api/services/ml/
├── inference.py        # Updated multi-image logic + filtering
├── model_loader.py     # Already loads Stage 1 & Stage 2
docs/phases/backend-integration-polish/
├── plan/2025-02-XX-backend-integration-polish-v1.0.md
├── implementation/README.md   (tbd)
├── test/README.md             (tbd)
```

---

## Testing Requirements

### Test Scenarios

#### Happy Path
1. **Multi-image inference**
   - Upload 2–3 images, call `/infer`, expect array of detection sets.
   - Verify each image preserves `image_id` and detection count.
2. **Filter intact parts**
   - Call `/infer?include_intact=false`, verify only damaged entries return.
3. **Estimate integration**
   - Feed filtered detections into `/estimate`; ensure cost calculations still succeed.

#### Edge Cases
1. Missing model file -> `/infer` returns 500 with descriptive error.
2. Empty `file_ids` array -> `/infer` returns 400.

#### Performance
1. Measure average latency across 10 samples (log or CLI output).

### Deliverables
- ✅ Updated API payload contract documented.
- ✅ Passing automated test script.
- ⚠️ Latency measurement deferred to future performance phase.

---

## Dependencies / Risks
- Need access to both YOLO weight files locally.
- Rely on current React app to adapt to new payload (coordinate with frontend phase).

---

## What "Done" Looks Like
- `/infer` now supports multi-image input, optional intact filtering, consistent payloads, and latency logging.
- Automated tests cover upload → infer (with/without intact) → estimate.
- Frontend devs can leverage `include_intact` to hide undamaged parts.

---
