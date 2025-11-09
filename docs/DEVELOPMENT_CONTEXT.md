# Development Context & Guidelines

**Last Updated:** 2025-11-04  
**Purpose:** This document captures the development context, guidelines, and key decisions made during the planning phase of the AI-Powered Auto Damage Estimator project. This helps maintain continuity across different machines and chat sessions.

---

## Development Workflow

We follow a strict **Plan → Implement → Test** cycle for all features:

1. **Plan**: Discuss feature ideas, create detailed plan document
2. **Implement**: Develop the feature according to the plan
3. **Test**: Comprehensive testing from user perspective (frontend + backend), covering happy paths, edge cases, and error scenarios

All plans are stored in `docs/plans/` following the `PLAN_TEMPLATE.md` format.

---

## Project Understanding

### Current State
- **Platform**: AI-powered web application for car damage detection and cost estimation
- **Tech Stack**: 
  - Backend: FastAPI (Python)
  - Frontend: Streamlit (to be imported)
  - ML Model: YOLOv8n (to be trained)
  - Storage: Supabase (free tier)
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
- **October (Weeks 3–6)**: Train YOLOv8, build backend APIs, Streamlit UI skeleton
- **Late October (Weeks 7–8)**: Integrate cost engine, severity rules, editing features
- **Early November (Week 9)**: Add VIN decode, GPT summary, polish UI
- **Mid-November (Week 10)**: Testing + Demo prep with sample reports

---

## Team Assignments

### Saad's Domain (Cost Estimation)
- **Step 1**: Define scope (parts, damage states, severity rules). Create `cost_rules.csv` with public labor/parts costs
- **Step 6**: Integrate severity scoring + cost engine (CSV-driven)
- **Step 5 (maybe)**: Streamlit UI cost estimate table integration

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

### API Endpoints (Planned)
- `POST /upload` - Upload car photos
- `POST /infer` - Run YOLOv8 inference on uploaded images
- `POST /estimate` - Calculate repair cost estimate
- `GET /report` - Get estimate report
- `POST /report/pdf` - Generate PDF report

### Dataset Requirements
- **Kaggle Datasets**: Car Damage Detection, Car Parts Segmentation (free, CC licenses)
- **Roboflow Universe**: Vehicle damage and parts datasets in YOLOv8 format (free tier)
- **Custom Labels**: 200–300 manually labeled images for missing parts & severity cases
- **Data Format**: YOLOv8-ready (`images/` + `labels/` folders + `data.yaml`)

### Cost Engine
- **CSV-driven**: `cost_rules.csv` with public labor/parts costs
- **Rules**: labor hours × labor rate, parts costs (new/used ranges), paint/material adders
- **Output**: Line-item estimate with totals (min/likely/max)

### Model Training
- **Model**: YOLOv8n (nano version for speed)
- **Training Platform**: Colab/Kaggle GPU (free tier)
- **Evaluation**: Hold-out set with mAP > 0.6 target
- **Parts to Detect**: 10–12 key car parts
- **Damage Types**: dent, scrape, crack, missing, intact

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
- ⏳ Frontend UI (to be imported)
- ⏳ Backend API (to be implemented)
- ⏳ ML model training (to be done)
- ⏳ Cost engine implementation (Saad - Step 6)

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

## Recent Achievements

### Initial Setup (2025-11-04)
- ✅ Project file structure created
- ✅ Documentation structure established
- ✅ Development context updated
- ✅ GitHub repository connected and initialized
- ✅ Cost rules CSV added by Saad (`data/auto_damage_repair_costs_MASTER.csv`)
- ✅ Initial commit pushed to remote repository

---

**Important:** This document is a living document. Update it as the project evolves to maintain continuity across different machines and chat sessions.
