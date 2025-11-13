# Feature Plan: Frontend Polish & UX Alignment

**Date:** 2025-02-XX  
**Phase:** Frontend Polish (Plan Step 5/7 follow-up)  
**Status:** ✅ Completed

---

## Feature Overview

### What It Does
Refines the React UI so it presents the new two-stage detections and cost estimates cleanly: only show relevant damages, align overlay boxes with the actual parts, and let user edits (severity, labor, OEM toggle) trigger real recalculations.

### Why It's Needed
- Current overlays draw large part boxes that overflow the image because we show Stage 1 boxes unmodified.
- Damage tables still list intact parts by default (Cursor added a toggle, but UX needs to be finalized).
- Editing severity/labor in the UI doesn’t call `/estimate`, so totals never change when the user tweaks values.

### User Story
As a user reviewing an estimate, I only want to see the damaged parts highlighted, adjust severity or parts preference, and immediately see updated costs and clean visuals.

---

## Technical Requirements

### UI/Frontend Changes
- [x] Overlay polish: only draw damaged parts for selected image, severity color coding, clipping to bounds. Use sample fixtures under `data/samples/images/` for regression.
- [x] Intact toggle: default hidden (cursor’s toggle retained).
- [x] Severity/Labor edits: re-run `/estimate` when user changes values.
- [x] OEM toggle: continues to call `/estimate` when preference changes.
- [ ] Optional: display backend metadata (filtered count, latency) – deferred.

### Backend/API Coordination
- [ ] No major API changes expected, but expose an endpoint or helper to re-run `/estimate` with modified detections (already supported).
- [ ] Confirm bounding-box coords provided by `/infer` are normalized vs. pixel; update frontend scaling formula if needed.

### Testing/Docs
- [x] Updated test checklist (see `docs/phases/frontend-polish/test/README.md`).
- [ ] Capture before/after screenshots (optional follow-up).

---

## Implementation Details

### Overlay Strategy
- Use Stage 1 bbox but intersect with image dimensions to prevent overflow.
- Optionally shrink boxes around Stage 2 detections by applying padding factor (configurable).
- Apply severity color map:
  - Minor → #FFD166
  - Moderate → #FB8500
  - Severe → #D90429

### Recalculation Flow
1. User edits severity or labor hours → update local state.
2. On “Recalculate” click, send modified detections to `/estimate`.
3. Update cost table + totals in response.

### File Structure (React app)
```
apps/web/src/components/DamageDetectionOverlay.tsx
apps/web/src/components/DamageAssessmentTable.tsx
apps/web/src/hooks/useEstimate.ts
```

---

## Testing Requirements

1. **Overlay accuracy**
   - Upload sample images (Car damages 102/127).
   - Verify boxes align with actual damaged panels and only appear for damaged parts.

2. **Intact toggle**
   - Ensure toggle hides/shows intact entries without reloading page.

3. **Severity/labor edits**
   - Change severity from “Moderate” → “Minor”.
   - Run “Recalculate” and confirm totals change (labor hours adjust).

4. **OEM toggle**
   - Toggle OEM vs. used; totals should change accordingly.

5. **UI regression**
   - Cost table scroll, PDF download, Save Draft still functional.

---

## Deliverables
- Updated React components with polished overlays and edit flows.
- UX doc/screenshots demonstrating the new behavior.
- Frontend test notes confirming the scenarios above.

---

## Out of Scope
- VIN decode, GPT summary (Plan Step 8) – explicitly postponed per latest decision.
- Additional ML training or backend cost tweaks (handled in prior phases).

---
