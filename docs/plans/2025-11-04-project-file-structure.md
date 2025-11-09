# System Plan: Project File Structure

**Date:** 2025-11-04  
**Phase:** Initial Setup  
**Status:** Planning

---

## Feature Overview

### What It Does
Establishes the complete file and directory structure for the AI-Powered Auto Damage Estimator project, organizing code, documentation, data, and infrastructure according to team assignments and project deliverables.

### Why It's Needed
- Clear separation of responsibilities (Saad: cost estimation, User: backend/ML)
- Organized structure for collaboration
- Consistent documentation and planning workflow
- Easy navigation and maintenance
- Foundation for scalable development

### User Story
As a developer, I want a well-organized project structure so that I can easily find files, understand the codebase, and collaborate effectively with my teammate.

---

## Technical Requirements

### Project Structure
- [ ] Create root-level directories (`apps/`, `docs/`, `infra/`, `data/`, `models/`)
- [ ] Set up backend structure (`apps/api/`)
- [ ] Set up frontend placeholder (`apps/web/` - for UI import)
- [ ] Create documentation structure (`docs/plans/`, `docs/data/`, etc.)
- [ ] Set up data directories for datasets and model artifacts
- [ ] Create infrastructure configuration files

### GitHub Setup
- [ ] Initialize/connect to existing repository
- [ ] Create `.gitignore` file
- [ ] Set up branch structure (if needed)
- [ ] Add README.md with project overview

### Documentation Structure
- [ ] Create `docs/plans/` for feature plans
- [ ] Create `docs/data/` for datasets and cost rules
- [ ] Create `docs/system/` for system-level documentation
- [ ] Update `DEVELOPMENT_CONTEXT.md` for this project

### File Organization by Assignment

#### Saad's Domain (Cost Estimation)
- [ ] `apps/api/services/cost_engine/` - Cost calculation logic
- [ ] `apps/api/services/severity/` - Severity scoring rules
- [ ] `data/cost_rules.csv` - Cost rules configuration
- [ ] `docs/data/cost_rules/` - Cost rules documentation

#### User's Domain (Backend/ML)
- [ ] `apps/api/` - FastAPI backend structure
- [ ] `apps/api/routes/` - API endpoints
- [ ] `apps/api/services/ml/` - Model inference service
- [ ] `models/` - Trained YOLOv8 models
- [ ] `data/datasets/` - Training datasets
- [ ] `docs/system/ml/` - ML model documentation

#### Shared/Integration
- [ ] `apps/api/services/integration/` - VIN decode, GPT summary
- [ ] `apps/api/models/` - Database models
- [ ] `apps/api/core/` - Shared utilities, config

---

## Implementation Details

### Architecture Approach
Following a modular structure similar to Ingerios project:
- **apps/**: Application code (backend API, frontend UI)
- **docs/**: All documentation, plans, and project context
- **infra/**: Infrastructure configuration (Docker, deployment)
- **data/**: Datasets, cost rules, and data files
- **models/**: Trained ML models and weights

### File Structure

```
Auto_Damage_Project/
├── .gitignore
├── README.md
├── apps/
│   ├── api/                          # FastAPI Backend (User)
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI app entry point
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py             # Configuration settings
│   │   │   ├── dependencies.py       # Shared dependencies
│   │   │   └── exceptions.py         # Custom exceptions
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── upload.py             # POST /upload
│   │   │   ├── infer.py              # POST /infer
│   │   │   ├── estimate.py           # POST /estimate
│   │   │   └── report.py             # GET /report, POST /report/pdf
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── ml/                   # ML Inference (User)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── model_loader.py   # YOLOv8 model loading
│   │   │   │   ├── inference.py      # Detection inference
│   │   │   │   └── preprocess.py     # Image preprocessing
│   │   │   ├── cost_engine/           # Cost Calculation (Saad)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── calculator.py     # Main cost calculation
│   │   │   │   ├── rules_loader.py   # Load cost_rules.csv
│   │   │   │   └── parts_cost.py     # Parts cost logic
│   │   │   ├── severity/              # Severity Scoring (Saad)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── scorer.py         # Severity classification
│   │   │   │   └── rules.py          # Severity rules
│   │   │   └── integration/           # External APIs (Shared)
│   │   │       ├── __init__.py
│   │   │       ├── vin_decode.py      # NHTSA VIN decode
│   │   │       └── gpt_summary.py     # GPT report summary
│   │   ├── models/                    # Database models (Shared)
│   │   │   ├── __init__.py
│   │   │   ├── detection.py           # Detection result models
│   │   │   ├── estimate.py            # Estimate models
│   │   │   └── report.py              # Report models
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── file_handler.py       # File upload handling
│   │       └── pdf_generator.py      # PDF report generation
│   └── web/                           # Streamlit Frontend (Placeholder)
│       ├── README.md                  # "UI files will be imported here"
│       └── .gitkeep                  # Keep directory in git
├── docs/
│   ├── DEVELOPMENT_CONTEXT.md        # Project context & workflow
│   ├── auto_damage_ai_project_plan.md # Main project plan
│   ├── PLAN_TEMPLATE.md              # Plan document template
│   ├── plans/                        # Feature/system plans
│   │   └── 2025-11-04-project-file-structure.md
│   ├── data/                         # Data documentation
│   │   ├── cost_rules/               # Cost rules documentation (Saad)
│   │   │   └── README.md
│   │   └── datasets/                 # Dataset documentation (User)
│   │       └── README.md
│   └── system/                       # System documentation
│       ├── ml/                       # ML model docs (User)
│       │   ├── model_training.md
│       │   └── inference_guide.md
│       └── api/                      # API documentation
│           └── endpoints.md
├── data/
│   ├── cost_rules.csv                # Cost rules (Saad)
│   ├── datasets/                     # Training datasets (User)
│   │   ├── images/
│   │   ├── labels/
│   │   └── data.yaml
│   └── test_images/                 # Test images for development
├── models/                           # Trained models (User)
│   ├── yolov8n_car_damage.pt        # Trained YOLOv8 model
│   └── README.md
├── infra/                            # Infrastructure
│   ├── docker/
│   │   ├── Dockerfile.api
│   │   └── docker-compose.yml
│   └── deployment/
│       └── README.md
└── requirements.txt                  # Python dependencies
```

### Component Breakdown

#### Backend API (`apps/api/`)
- **main.py**: FastAPI application initialization, middleware, route registration
- **core/**: Shared configuration, dependencies, exception handling
- **routes/**: API endpoint definitions (upload, infer, estimate, report)
- **services/ml/**: YOLOv8 model loading, inference, image preprocessing
- **services/cost_engine/**: Cost calculation using CSV rules (Saad)
- **services/severity/**: Damage severity classification (Saad)
- **services/integration/**: External API integrations (VIN decode, GPT)
- **models/**: Pydantic/SQLAlchemy models for data structures
- **utils/**: Helper functions (file handling, PDF generation)

#### Frontend (`apps/web/`)
- Placeholder directory for Streamlit UI files
- Will be populated when UI files are imported

#### Documentation (`docs/`)
- **plans/**: All feature and system plan documents
- **data/**: Documentation for datasets and cost rules
- **system/**: Technical documentation (ML, API)

#### Data (`data/`)
- **cost_rules.csv**: CSV file with labor hours, parts costs, paint/material adders (Saad)
- **datasets/**: YOLOv8 formatted training data (images/, labels/, data.yaml)
- **test_images/**: Sample images for development/testing

#### Models (`models/`)
- Trained YOLOv8 model weights
- Model metadata and versioning

### Data Flow

1. **Upload**: User uploads images → `routes/upload.py` → `utils/file_handler.py` → Store files
2. **Inference**: Stored images → `routes/infer.py` → `services/ml/inference.py` → YOLOv8 model → Detection results
3. **Severity**: Detection results → `services/severity/scorer.py` → Severity classification (Saad)
4. **Estimate**: Detection + Severity → `routes/estimate.py` → `services/cost_engine/calculator.py` → Cost calculation using `cost_rules.csv` (Saad)
5. **Report**: Estimate data → `routes/report.py` → `utils/pdf_generator.py` → PDF export

---

## Deliverables

### Final Output
- Complete project directory structure
- All necessary placeholder files and directories
- `.gitignore` configured for Python/ML project
- `README.md` with project overview and setup instructions
- `DEVELOPMENT_CONTEXT.md` updated for Auto_Damage_Project
- Documentation structure ready for feature plans

### Acceptance Criteria
- [ ] All directories created according to structure
- [ ] GitHub repository connected and `.gitignore` configured
- [ ] Frontend placeholder directory created with README
- [ ] Documentation structure in place (`docs/plans/`, `docs/data/`, `docs/system/`)
- [ ] Data directories ready (`data/cost_rules.csv` placeholder, `data/datasets/`)
- [ ] Models directory created
- [ ] Infrastructure directory structure created
- [ ] `requirements.txt` placeholder created
- [ ] `DEVELOPMENT_CONTEXT.md` updated for this project

### What "Done" Looks Like
A fully structured project directory that:
- Clearly separates Saad's work (cost estimation) from User's work (backend/ML)
- Has placeholders for all major components
- Includes documentation structure following the Plan → Implement → Test workflow
- Is ready for code implementation and UI import
- Has GitHub integration configured

---

## Dependencies

### Prerequisites
- [ ] GitHub repository already created (confirmed)
- [ ] Project plan document exists (`auto_damage_ai_project_plan.md`)
- [ ] Development workflow understood (Plan → Implement → Test)

### Blockers
- None identified

---

## Notes

### Team Assignments Summary

**Saad's Responsibilities:**
- Step 1: Define scope, create `cost_rules.csv`
- Step 6: Integrate severity scoring + cost engine
- Step 5 (maybe): Streamlit UI cost estimate table integration

**User's Responsibilities:**
- Step 2-3: Dataset collection, labeling, YOLOv8 training
- Step 4: FastAPI backend (`/upload`, `/infer`, `/estimate`, `/report`)
- Step 7-8: User edits, VIN decode, GPT summary
- Backend integration and ML inference

### Key Decisions
1. **Structure follows Ingerios pattern**: `apps/`, `docs/`, `infra/` for consistency
2. **Clear separation**: Cost estimation logic in `services/cost_engine/` and `services/severity/` (Saad)
3. **ML services isolated**: `services/ml/` for model-related code (User)
4. **Documentation mirrors code structure**: `docs/data/cost_rules/` for Saad, `docs/system/ml/` for User
5. **Frontend placeholder**: `apps/web/` with README explaining UI import

### GitHub Considerations
- `.gitignore` should exclude: `__pycache__/`, `*.pyc`, `.env`, `models/*.pt` (large files), `data/datasets/` (large datasets)
- Consider Git LFS for model files if needed
- Branch strategy: main branch, feature branches per assignment

### Future Considerations
- When UI is imported, it will go into `apps/web/`
- Model training scripts can go in `scripts/` or `docs/system/ml/`
- Database setup (if needed) will go in `infra/` or `apps/api/core/`

---

## Implementation Status

### Completed
- [ ] Plan document created

### In Progress
- [ ] Directory structure creation
- [ ] GitHub setup

### Pending
- [ ] Create all directories
- [ ] Create placeholder files
- [ ] Configure `.gitignore`
- [ ] Create/update `README.md`
- [ ] Update `DEVELOPMENT_CONTEXT.md`
- [ ] Initialize GitHub connection

---

## Changes from Original Plan

_To be updated during implementation if needed_

---

**Remember:** This structure is the foundation. It should be flexible enough to accommodate changes while maintaining clear organization and separation of responsibilities.

