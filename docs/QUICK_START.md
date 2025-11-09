# Quick Start Guide

**For switching to another computer or starting a new session**

## Initial Setup on New Computer

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ArgusOnline-dev/Auto_Damage_Detector.git
   cd Auto_Damage_Detector
   ```

2. **Read the development context:**
   - Open and read `docs/DEVELOPMENT_CONTEXT.md` first
   - This contains all project context, team assignments, and workflow

3. **Review project plan:**
   - Check `docs/auto_damage_ai_project_plan.md` for overall project plan
   - Check `docs/plans/` for specific feature plans

4. **Set up environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

## Current Project Status

### ✅ Completed
- Project file structure created
- Documentation structure established
- Cost rules CSV added by Saad (`data/auto_damage_repair_costs_MASTER.csv`)
- GitHub repository connected and synced

### ⏳ In Progress / Next Steps
- Frontend UI (to be imported)
- Backend API (to be implemented)
- ML model training (to be done)
- Cost engine implementation (Saad - Step 6)

## Team Assignments

### Your Domain (Backend/ML)
- **Step 2-3**: Dataset collection, labeling, YOLOv8 training
- **Step 4**: Build FastAPI backend (`/upload`, `/infer`, `/estimate`, `/report`)
- **Step 7-8**: User edits, VIN decode, GPT summary

### Saad's Domain (Cost Estimation)
- **Step 1**: ✅ DONE - Cost rules CSV created
- **Step 6**: Integrate severity scoring + cost engine
- **Step 5 (maybe)**: Streamlit UI cost estimate table integration

## Recommended Next Steps

### Option 1: Start with FastAPI Backend (Step 4)
**Why:** Builds foundational infrastructure, allows parallel work with Saad
- Create FastAPI app structure (`apps/api/main.py`)
- Set up API routes (`/upload`, `/infer`, `/estimate`, `/report`)
- Create placeholder/mock responses until model is trained
- Set up file upload handling
- Integrate with cost rules CSV (Saad's work)

**Files to create:**
- `apps/api/main.py` - FastAPI app
- `apps/api/routes/upload.py` - File upload endpoint
- `apps/api/routes/infer.py` - ML inference endpoint (placeholder)
- `apps/api/routes/estimate.py` - Cost estimation endpoint
- `apps/api/routes/report.py` - Report generation endpoint
- `apps/api/core/config.py` - Configuration
- `apps/api/utils/file_handler.py` - File handling utilities

### Option 2: Start with Dataset Collection (Step 2-3)
**Why:** Model training takes time, good to start early
- Collect datasets from Kaggle/Roboflow
- Set up YOLOv8 data structure (`data/datasets/`)
- Label 200-300 custom images
- Prepare for training on Colab/Kaggle

**Files to create:**
- `data/datasets/data.yaml` - Dataset configuration
- `docs/system/ml/model_training.md` - Training documentation
- Training scripts (can be in Colab/Kaggle notebooks)

## Workflow Reminder

Always follow **Plan → Implement → Test** cycle:
1. **Plan**: Create plan document in `docs/plans/` using `PLAN_TEMPLATE.md`
2. **Implement**: Develop according to plan
3. **Test**: Comprehensive testing from user perspective

## Quick Commands

```bash
# Pull latest changes
git pull origin main

# Check status
git status

# View recent commits
git log --oneline -5

# Create new branch for feature
git checkout -b feature/your-feature-name
```

---

**Remember:** Always read `docs/DEVELOPMENT_CONTEXT.md` first when starting a new session!

