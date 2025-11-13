# Development Context & Guidelines

**Last Updated:** 2025-01-XX  
**Purpose:** This document captures the development context, guidelines, and key decisions made during the planning phase of the AI-Powered Auto Damage Estimator project. This helps maintain continuity across different machines and chat sessions.

---

## Development Workflow

We follow a strict **Plan → Implement → Test** cycle for all features:

1. **Plan**: Discuss feature ideas, create detailed plan document
2. **Implement**: Develop the feature according to the plan
3. **Test**: Comprehensive testing from user perspective (frontend + backend), covering happy paths, edge cases, and error scenarios

All active plans live under `docs/phases/<phase>/plan/` using the shared `PLAN_TEMPLATE.md`.

---

## Project Understanding

### Current State
- **Platform**: AI-powered web application for car damage detection and cost estimation
- **Tech Stack**: 
  - Backend: FastAPI (Python) ✅ **Implemented**
  - Frontend: React + Vite + TypeScript ✅ **Integrated**
  - ML Model: YOLOv8n ✅ **Trained** (150 epochs, mAP50: 0.7+)
  - Storage: Temporary file storage (in-memory for reports)
  - Infrastructure: Docker (planned)

### Key Features Planned
1. **Photo Upload** - Users can upload multiple car photos (front, sides, rear)
2. **Damage Detection** - YOLOv8 model detects 10–12 key parts and labels damage type (dent, scrape, crack, missing, intact)
3. **Severity Classification** - Damage severity bucketed into minor, moderate, or severe using rules
4. **Cost Estimation** - CSV-driven rules: labor hours × labor rate, parts costs (new/used ranges), paint/material adders
5. **Report Generation** - Line-item estimate with totals (min/likely/max). Export as PDF
6. **Explainability** - Transparent mapping from detection → severity → cost rules. Optional GPT summary for human-readable report
7. **User Input** - Users can set labor rate, toggle OEM/Used parts, and edit severity for accuracy

### Project Timeline
- **September (Weeks 1–2)**: Scope, cost_rules.csv, dataset collection & labeling
- **October (Weeks 3–6)**: Train YOLOv8, build backend APIs, React frontend integration ✅ **Completed**
- **Late October (Weeks 7–8)**: Integrate cost engine, severity rules, editing features
- **Early November (Week 9)**: Add VIN decode, GPT summary, polish UI
- **Mid-November (Week 10)**: Testing + Demo prep with sample reports

---

## Team Assignments

### Saad's Domain (Cost Estimation)
- **Step 1**: Define scope (parts, damage states, severity rules). Create `cost_rules.csv` with public labor/parts costs
- **Step 6**: Integrate severity scoring + cost engine (CSV-driven)
- **Step 5 (maybe)**: React UI cost estimate table integration ✅ **Completed**

**Files/Directories:**
- `apps/api/services/cost_engine/` - Cost calculation logic
- `apps/api/services/severity/` - Severity scoring rules
- `data/cost_rules.csv` - Cost rules configuration
- `docs/data/cost_rules/` - Cost rules documentation

### User's Domain (Backend/ML)
- **Step 2-3**: Assemble datasets from Kaggle/Roboflow. Label 200–300 custom images in YOLOv8 format. Train YOLOv8n (Colab/Kaggle GPU). Evaluate on hold-out set (mAP > 0.6)
- **Step 4**: Build FastAPI backend: `/upload`, `/infer`, `/estimate`, `/report`
- **Step 7-8**: Add user edits (severity dropdown, OEM/Used toggle). Add VIN decode (NHTSA API) and optional GPT summary
- Backend integration and ML inference

**Files/Directories:**
- `apps/api/` - FastAPI backend structure
- `apps/api/routes/` - API endpoints
- `apps/api/services/ml/` - Model inference service
- `models/` - Trained YOLOv8 models
- `data/datasets/` - Training datasets
- `docs/system/ml/` - ML model documentation

### Shared/Integration
- `apps/api/services/integration/` - VIN decode, GPT summary
- `apps/api/models/` - Database models
- `apps/api/core/` - Shared utilities, config

---

## Key Technical Decisions

### File Structure
Following a modular structure similar to Ingerios project:
- **apps/**: Application code (backend API, frontend UI)
- **docs/**: All documentation, plans, and project context
- **infra/**: Infrastructure configuration (Docker, deployment)
- **data/**: Datasets, cost rules, and data files
- **models/**: Trained ML models and weights

### API Endpoints (Implemented ✅)
- `POST /api/v1/upload` - Upload car photos (✅ Implemented)
- `POST /api/v1/infer` - Run YOLOv8 inference on uploaded images (✅ Implemented - currently mock data)
- `POST /api/v1/estimate` - Calculate repair cost estimate (✅ Implemented)
- `GET /api/v1/report/{report_id}` - Get estimate report (✅ Implemented)
- `POST /api/v1/report/pdf` - Generate PDF report (✅ Implemented)
- `GET /api/v1/health` - Health check endpoint (✅ Implemented)

### Dataset Requirements ✅ (Completed)
- **Source Dataset**: Supervisely-format dataset with polygon annotations ✅ **Converted**
- **Conversion Tool**: Custom converter script (`tools/datasets/convert_supervisely_to_yolov8_detection.py`) ✅ **Created**
- **Final Format**: YOLOv8-ready (`images/` + `labels/` folders + `data.yaml`) ✅ **Generated**
- **Dataset Size**: 1,000+ images processed and split (train/val/test: 70/20/10) ✅ **Completed**
- **Location**: `data/datasets/processed/yolov8_detection/` ✅ **Ready for training**

### Cost Engine
- **CSV-driven**: `cost_rules.csv` with public labor/parts costs
- **Rules**: labor hours × labor rate, parts costs (new/used ranges), paint/material adders
- **Output**: Line-item estimate with totals (min/likely/max)

### Model Training ✅ (Completed)
- **Model**: YOLOv8n (nano version for speed) ✅ **Trained**
- **Training Platform**: Local GPU (RTX 4070 Ti) ✅ **Completed**
- **Evaluation**: Hold-out set with mAP > 0.6 target ✅ **Achieved mAP50: 0.7+**
- **Training Status**: 150 epochs completed, model weights saved
- **Parts to Detect**: 10–12 key car parts (from dataset)
- **Damage Types**: dent, scrape, crack, missing, intact (from dataset)
- **Next Step**: Integrate trained model into FastAPI backend

### External APIs
- **NHTSA API**: VIN decode (free)
- **OpenAI API**: GPT summary for human-readable reports (optional, ~$0.0003/request)

---

## Testing Philosophy

### Test Phase Requirements
- Perform tests from user's perspective (frontend + backend)
- Cover happy paths, edge cases, and error scenarios
- Provide comprehensive feedback including:
  - Internal observations (logs, terminal output)
  - External observations (UI behavior, user experience)
- Goal: Minimize manual testing and iterative feedback

### Testing Approach
- Test all API endpoints
- Test all UI workflows
- Test error handling
- Test edge cases (large files, invalid data, API failures)
- Test performance (model inference speed, report generation)

---

## Notes for Future Development

### Current Implementation Status
- ✅ Project structure created
- ✅ Documentation structure in place
- ✅ Cost rules CSV created by Saad (`data/auto_damage_repair_costs_MASTER.csv`)
- ✅ **FastAPI Backend Foundation** - Complete (all endpoints, models, services)
- ✅ **Frontend-Backend Integration** - Complete (React frontend connected via Vite proxy)
- ✅ **ML Model Training** - Complete (dataset conversion, YOLOv8n trained 150 epochs)
- ✅ **Dataset Conversion Tools** - Complete (Supervisely to YOLOv8 converter)
- ✅ **Comprehensive Documentation** - Complete (training guides, explainers, integration docs)
- ⏳ Cost engine implementation (Saad - Step 6)
- ⏳ ML model integration into backend (pending)
- ⏳ LLM integration (Step 7-8, placeholder for later)

### Future Enhancements
- Database integration (if needed for storing estimates)
- User authentication (if needed)
- Advanced explainability features
- Mobile app version
- Integration with insurance companies

---

## How to Use This Document

When switching to another computer or starting a new chat session:

1. **Read this document first** - Understand the project context and guidelines
2. **Review the plan documents** - Check `docs/plans/` for feature plans
3. **Review the project plan** - Check `docs/auto_damage_ai_project_plan.md` for overall project plan
4. **Review development workflow** - Follow the Plan → Implement → Test cycle

This document should be updated whenever:
- Major decisions are made
- New features are planned
- Development guidelines change
- Key technical decisions are made

---

## Completed Phases

### Phase 1: FastAPI Backend Foundation ✅ (2025-11-05)
**Status:** Complete - All tests passed (11/11)

**What Was Built:**
- Complete FastAPI backend with all core endpoints
- File upload handling with validation (`/api/v1/upload`)
- ML inference endpoint with mock data (`/api/v1/infer`)
- Cost estimation endpoint (`/api/v1/estimate`)
- PDF report generation (`/api/v1/report/pdf`)
- Health check endpoint (`/api/v1/health`)
- Pydantic models for all request/response types
- File handler with image validation
- PDF generator using ReportLab
- Service interfaces for ML, cost engine, and severity scoring
- Comprehensive error handling and custom exceptions
- Auto-generated API documentation (Swagger/ReDoc)

**Key Files:**
- `apps/api/main.py` - FastAPI application
- `apps/api/routes/` - All API endpoints
- `apps/api/models/` - Pydantic models
- `apps/api/services/` - Service interfaces
- `apps/api/utils/` - File handling and PDF generation
- `run.py` - Server startup script

**Documentation:**
- `docs/phases/fastapi-backend-foundation/implementation/implementation_log.md`
- `docs/phases/fastapi-backend-foundation/test/test_results.md`
- `docs/phases/fastapi-backend-foundation/plan/2025-11-05-fastapi-backend-foundation-v1.0.md`

---

### Phase 2: Frontend-Backend Integration ✅ (2025-11-05)
**Status:** Complete - Full workflow tested and working

**What Was Built:**
- React frontend integrated with FastAPI backend
- Vite proxy configuration for API requests (`/api` → `http://localhost:8000`)
- API client library (`apps/web/src/lib/api.ts`)
- Updated Upload page with real API calls
- Data mapping between frontend and backend formats
- Error handling and user feedback
- Server startup scripts (`scripts/run_frontend.py`, `scripts/run_backend.py`)

**Key Features:**
- Image upload to backend
- Real-time inference calls
- Cost estimation with labor rate and parts preference
- PDF report generation and download
- Complete end-to-end workflow

**Key Files:**
- `apps/web/vite.config.ts` - Proxy configuration
- `apps/web/src/lib/api.ts` - API client
- `apps/web/src/pages/Upload.tsx` - Main upload page (updated)
- `scripts/run_frontend.py` - Frontend startup script
- `run_all.py` - Combined server startup

**Documentation:**
- `docs/phases/fastapi-backend-foundation/INTEGRATION_GUIDE.md`
- `docs/phases/fastapi-backend-foundation/START_SERVERS.md`
- `docs/phases/fastapi-backend-foundation/test/test_integration.py`

---

### Phase 3: ML Model Training ✅ (2025-01-XX)
**Status:** Complete - YOLOv8n trained successfully (150 epochs, mAP50: 0.7+)

**What Was Built:**
- Dataset converter: Supervisely JSON → YOLOv8 detection format
- Processed dataset with train/val/test splits (70/20/10)
- YOLOv8n model trained locally on RTX 4070 Ti
- Training completed: 150 epochs with early stopping
- Model evaluation and validation metrics
- Visual prediction outputs for verification

**Dataset Conversion:**
- Converted polygon annotations to bounding boxes
- Normalized coordinates for YOLOv8 format
- Generated `data.yaml` with absolute paths
- Split dataset into train/val/test sets
- Created class mapping and labels

**Training Results:**
- **Model:** YOLOv8n (nano)
- **Epochs:** 150 (with patience=50)
- **Batch Size:** 24
- **Image Size:** 640x640
- **Device:** CUDA (RTX 4070 Ti)
- **Final mAP50:** 0.7+ (exceeded 0.6 target)
- **Training Time:** ~15 minutes for 150 epochs

**Key Files:**
- `tools/datasets/convert_supervisely_to_yolov8_detection.py` - Converter script
- `tools/datasets/README.md` - Converter documentation
- `data/datasets/processed/yolov8_detection/` - Processed dataset
- `runs/yolov8_det/car-damage-v13/weights/best.pt` - Trained model weights
- `runs/yolov8_det/car-damage-v13/` - Training artifacts and metrics

**Documentation:**
- `docs/phases/ml-model-training/TRAINING_EXPLAINER.md` - Comprehensive training guide
- `docs/phases/ml-model-training/YOLOV8_TRAINING_GUIDE.md` - Setup and training steps
- `docs/phases/ml-model-training/QA_SUMMARY.md` - Q&A about training
- `docs/phases/ml-model-training/plan/2025-01-XX-ml-model-training-v1.0.md` - Training plan

---

## Recent Achievements

### Initial Setup (2025-11-04)
- ✅ Project file structure created
- ✅ Documentation structure established
- ✅ Development context updated
- ✅ GitHub repository connected and initialized
- ✅ Cost rules CSV added by Saad (`data/auto_damage_repair_costs_MASTER.csv`)
- ✅ Initial commit pushed to remote repository

### FastAPI Backend Foundation (2025-11-05)
- ✅ Complete FastAPI backend implemented
- ✅ All API endpoints functional
- ✅ File upload, inference, estimation, and report generation working
- ✅ Comprehensive test suite (11/11 tests passed)
- ✅ API documentation auto-generated

### Frontend-Backend Integration (2025-11-05)
- ✅ React frontend integrated with FastAPI backend
- ✅ Vite proxy configured for seamless API communication
- ✅ Complete upload → inference → estimate → report workflow functional
- ✅ Error handling and user feedback implemented
- ✅ Integration testing completed

### ML Model Training (2025-01-XX)
- ✅ Dataset converter created (Supervisely → YOLOv8)
- ✅ Dataset processed and organized (1,000+ images)
- ✅ YOLOv8n model trained locally on RTX 4070 Ti
- ✅ Training completed: 150 epochs, mAP50: 0.7+
- ✅ Model weights and artifacts saved
- ✅ Comprehensive training documentation created
- ✅ All training files committed to GitHub

---

**Important:** This document is a living document. Update it as the project evolves to maintain continuity across different machines and chat sessions.
