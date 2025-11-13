# 🚗 AI-Powered Auto Damage Estimator

An AI-powered web application that detects car damage from uploaded photos and generates transparent repair cost estimates.

## 🧩 Overview

The current MVP focuses on consumers and small businesses that need quick, explainable repair estimates. The backend (FastAPI) runs a two-stage YOLOv8 pipeline (parts + damage) and a CSV-driven cost engine. The frontend (React + Vite + Tailwind) lets users upload photos, review detections, tweak severity/labor/OEM settings, and export PDF reports.

## ⚙️ Implemented Features

- **Uploads**: Drag-and-drop multiple photos; optional toggle to show intact parts.
- **Detection**: Stage 1 YOLO detects body parts; Stage 2 YOLO assigns damage classes (`dent`, `scratch`, `cracked`, `missing_part`, etc.).
- **Severity**: Backend heuristics map damage type + confidence to `minor/moderate/severe`, but users can override and re-run estimates instantly.
- **Cost Engine**: `data/auto_damage_repair_costs_MASTER.csv` drives labor hours, parts cost (OEM vs used), and totals (min/likely/max).
- **Reports**: Downloadable PDF showing detections, line items, and totals. “Save draft” currently stores data locally (browser `localStorage`).
- **Explainability**: API response includes each detection’s part/damage/severity plus filtered counts so the frontend can show only what matters.

## 🛠️ Tech Stack

| Area        | Technology                                  |
|-------------|---------------------------------------------|
| Backend     | FastAPI, Pydantic v2, Uvicorn               |
| Frontend    | React 18, Vite, TypeScript, Tailwind CSS    |
| ML          | YOLOv8n (Ultralytics) – two-stage pipeline  |
| Storage     | Local filesystem (uploads, models)          |
| Docs/Plans  | `docs/phases/<phase>/plan|implementation|test` |

VIN decode / GPT summary are **out of scope** for this MVP.

## 📁 Project Structure

```
Auto_Damage_Detector/
├── apps/
│   ├── api/                  # FastAPI backend
│   │   ├── core/             # config, exceptions
│   │   ├── routes/           # /upload, /infer, /estimate, /report
│   │   ├── services/
│   │   │   ├── ml/           # two-stage model loader + inference
│   │   │   ├── cost_engine/  # CSV-driven cost calculator
│   │   │   └── severity/     # severity heuristics
│   │   └── utils/            # file handling, PDF helpers
│   └── web/                  # React frontend (Vite)
├── data/                     # datasets + cost rules
├── models/                   # YOLO weight files (not in git)
├── docs/                     # context + per-phase plans/tests
└── requirements.txt          # backend deps
```

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node 18+ and `pnpm` (or npm/yarn if you prefer)

### Backend Setup
```bash
cd Auto_Damage_Detector
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
uvicorn apps.api.main:app --reload
```

Environment variables (optional) live in `.env`. Useful overrides:
```
PART_MODEL_PATH=models/yolov8n_part_detector.pt
DAMAGE_MODEL_PATH=models/yolov8n_damage.pt
COST_RULES_PATH=data/auto_damage_repair_costs_MASTER.csv
```

### Frontend Setup
```bash
cd Auto_Damage_Detector/apps/web
pnpm install        # or npm install
pnpm dev            # starts Vite dev server
```

The frontend expects the backend at `http://localhost:8000`. Adjust `VITE_API_BASE_URL` in `apps/web/.env` if needed.

## ✅ Tests

Two end-to-end scripts exercise backend+frontend contracts. Run them while the backend is up:

```bash
# Multi-image inference + intact filtering + /estimate
python docs/phases/ml-model-training/test/test_two_stage_integration.py

# Cost engine + severity overrides + OEM toggle
python docs/phases/cost-engine-integration/test/test_cost_engine.py
```

Each script logs PASS/FAIL along with totals. Detailed instructions/results live in the respective `docs/phases/**/test/README.md`.

## 📚 Documentation
- Development context & workflow: `docs/DEVELOPMENT_CONTEXT.md`
- Per-phase plans/impl/tests: `docs/phases/<phase>/`
- Cost rules CSV: `data/auto_damage_repair_costs_MASTER.csv`

## 📝 License

TBD — choose the license you need before publishing.

---

Status: MVP features implemented (two-stage detection, severity rules, cost engine, React UI). Remaining nice-to-haves: VIN/GPT, real draft/report persistence, optional frontend polish items noted in `docs/phases/frontend-polish/`.

