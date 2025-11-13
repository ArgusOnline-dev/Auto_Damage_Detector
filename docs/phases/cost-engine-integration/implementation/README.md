# Cost & Severity Engine Integration – Implementation Notes

**Date:** 2025-02-XX  
**Status:** In Progress

## Completed
- Severity mapper now assigns deterministic `minor/moderate/severe` values based on damage type + confidence (with user override support).
- Cost engine loads `data/auto_damage_repair_costs_MASTER.csv`, maps detection parts/damage types to CSV rows, and computes labor + parts totals (OEM vs. used).
- `/estimate` accepts `car_type` (default `Super`) so different rule sets can be used later.

## Details
- Mapping examples:
  - Stage damage `scratch`, `paint_chip`, `flaking`, `corrosion` → CSV `Scrape`
  - `cracked` → `Crack`
  - `broken_part` / `missing_part` → `Missing`
  - `dent` → `Dent`
- Parts are normalized via dictionary (e.g., `front_bumper` → `Front bumper`, `back_wheel` → `Wheel`).
- Unknown combinations fall back to defaults (logs warning) so `/estimate` never crashes.

## Remaining TODOs
- Unit tests for mapping/lookup helpers.
- Allow car_type selection from UI (currently hard-coded to “Super”).
- Update frontend to consume real severity/cost data.
