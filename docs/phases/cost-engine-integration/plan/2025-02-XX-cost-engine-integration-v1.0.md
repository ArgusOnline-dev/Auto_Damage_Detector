# Feature Plan: Cost & Severity Engine Integration

**Date:** 2025-02-XX  
**Phase:** Cost Engine Integration (Plan Step 6/7)  
**Status:** Planning

---

## Feature Overview

### What It Does
Connects Saad’s CSV-driven cost/severity logic to the live detection pipeline so `/estimate` returns real labor + parts totals based on the detected part/damage combinations. Replaces the placeholder mock data with real rules from `data/auto_damage_repair_costs_MASTER.csv`.

### Why It's Needed
- The UI now shows real part + damage detections, but severity and cost numbers are still hard-coded.
- Saad’s CSV already captures labor hours, parts costs, and severity rules; integrating it makes `/estimate` meaningful for users and unlocks report generation/VIN/GPT phases.

### User Story
As a user, when I upload photos and hit “Estimate,” I want the backend to calculate real-world repair costs based on detected parts/damage types, labor rates, and OEM vs. used parts preferences.

---

## Technical Requirements

### Backend Changes
- [ ] Implement a severity-mapping module that converts Stage 2 damage classes + confidence into severity buckets (minor/moderate/severe) according to CSV thresholds/rules.
- [ ] Parse `data/auto_damage_repair_costs_MASTER.csv` into an in-memory lookup keyed by `Part`, `Damage_Type`, `Severity`. Support car-type field (default to “Super” unless specified).
- [ ] Map Stage 2 damage classes (`dent`, `scratch`, `cracked`, `broken_part`, `missing_part`, `paint_chip`, `flaking`, `corrosion`, `intact`) to the CSV’s `Damage_Type` values (`Dent`, `Scrape`, `Crack`, `Missing`).
- [ ] Replace `calculate_cost` placeholder with real logic:
  - Multiply labor hours × selected labor rate.
  - Choose OEM vs. used part cost based on request flag.
  - Return totals (min/likely/max) consistent with CSV rules.
- [ ] Update `/estimate` response schema if needed (e.g., include `car_type`, `parts_source`, `severity_source` metadata).

### Frontend Changes (coordination)
- [ ] Confirm severity dropdown defaults align with backend output (users can override).
- [ ] Ensure OEM/used toggle matches backend flag names.

### Testing/Docs
- [ ] Unit tests for the cost engine (mapping from detection → CSV row).
- [ ] Update integration test script to run `/estimate` and verify totals change when toggling OEM/used.
- [ ] Document CSV mapping assumptions in `docs/phases/cost-engine-integration/`.

### API Endpoints
| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| POST | `/api/v1/estimate` | Uses real severity + cost rules | Planned update |

---

## Implementation Details

### Mapping Strategy
- Damage class mapping:
  - `dent` → `Dent`
  - `scratch`, `paint_chip`, `flaking`, `corrosion` → `Scrape` (or split if Saad provided specific columns)
  - `cracked` → `Crack`
  - `broken_part`, `missing_part` → `Missing`
  - `intact` → ignored/skipped
- Severity assignment:
  - Start with Stage 2 `confidence` thresholds (e.g., >0.8 severe, 0.5–0.8 moderate, else minor) or use deterministic rules from Saad’s doc if available.
  - Allow the frontend to override via the existing severity dropdown.

### Flow
1. `/infer` returns detections.
2. `/estimate` receives `detections` array + user inputs (`labor_rate`, `use_oem_parts`, optional `car_type`).
3. Severity mapper assigns severity to each detection if not provided.
4. Cost engine looks up matching CSV row, computes labor + parts totals.
5. Response includes detailed line items + aggregated totals (min/likely/max).

### File Structure
```
apps/api/services/severity/
├── interface.py        # replaced with real severity mapper
apps/api/services/cost_engine/
├── interface.py        # replaced with CSV-driven implementation
data/auto_damage_repair_costs_MASTER.csv
docs/phases/cost-engine-integration/
├── plan/2025-02-XX-cost-engine-integration-v1.0.md
├── implementation/README.md
├── test/README.md
```

---

## Testing Requirements

### Scenarios
1. **Happy path:** detections with multiple damage types produce correct line items and totals.
2. **OEM vs. used toggle:** same detections produce different totals when `use_oem_parts` changes.
3. **Unknown combination:** detection not present in CSV returns graceful fallback (e.g., default labor hours/parts cost or error message).
4. **Severity overrides:** when frontend supplies severity explicitly, backend respects it.

### Tests to Add
- Unit tests for mapping function (damage class → CSV damage type).
- Unit tests for CSV lookup (part + damage + severity).
- Updated integration script to compare OEM vs. used totals.

---

## Dependencies / Risks
- CSV needs to remain in sync (if Saad updates it, we must reload). Consider caching + reload trigger.
- Stage 2 damage classes must be mapped carefully; misalignment will produce zero matches.

---

## Deliverables
- Production-ready severity + cost engine integrated into `/estimate`.
- Documentation describing damage/severity mapping.
- Updated automated tests covering OEM vs. used scenarios.

---

## Next Steps After This Phase
- Expose car type selection (if needed).
- Generate PDFs/report summaries using real cost data.
- Proceed to VIN decode & GPT summary features.

---
