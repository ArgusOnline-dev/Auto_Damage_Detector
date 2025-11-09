# 🚗 AI-Powered Auto Damage Estimator

An AI-powered web application that detects car damages from uploaded photos and generates transparent repair cost estimates.

## 🧩 Overview

This project aims to build an MVP that focuses on consumers and small businesses (mechanic shops, towing companies, rental fleets), emphasizing **transparency, explainability, and affordability**.

## ⚙️ Features

- **Upload**: Users can upload multiple car photos (front, sides, rear)
- **Detection**: YOLOv8 model detects 10–12 key parts and labels damage type (dent, scrape, crack, missing, intact)
- **Severity**: Damage severity bucketed into minor, moderate, or severe using rules
- **Cost Engine**: CSV-driven rules: labor hours × labor rate, parts costs (new/used ranges), paint/material adders
- **Report**: Line-item estimate with totals (min/likely/max). Export as PDF
- **Explainability**: Transparent mapping from detection → severity → cost rules. Optional GPT summary for human-readable report
- **User Input**: Users can set labor rate, toggle OEM/Used parts, and edit severity for accuracy

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Streamlit
- **ML Model**: YOLOv8n (trained on Kaggle/Roboflow datasets)
- **Storage**: Supabase (free tier)
- **APIs**: NHTSA (VIN decode), OpenAI (optional GPT summaries)

## 📁 Project Structure

```
Auto_Damage_Project/
├── apps/
│   ├── api/              # FastAPI Backend
│   │   ├── core/         # Configuration, dependencies
│   │   ├── routes/       # API endpoints
│   │   ├── services/     # Business logic
│   │   │   ├── ml/       # ML inference (User)
│   │   │   ├── cost_engine/  # Cost calculation (Saad)
│   │   │   ├── severity/     # Severity scoring (Saad)
│   │   │   └── integration/   # External APIs (Shared)
│   │   ├── models/       # Database models
│   │   └── utils/        # Utility functions
│   └── web/              # Streamlit Frontend (placeholder)
├── docs/                 # Documentation
│   ├── plans/            # Feature/system plans
│   ├── data/             # Data documentation
│   └── system/          # Technical documentation
├── data/                 # Data files
│   ├── cost_rules.csv    # Cost estimation rules (Saad)
│   └── datasets/         # Training datasets (User)
├── models/               # Trained ML models
└── infra/                # Infrastructure configs
```

## 👥 Team Assignments

### Saad's Domain (Cost Estimation)
- Step 1: Define scope, create `cost_rules.csv`
- Step 6: Integrate severity scoring + cost engine
- Step 5 (maybe): Streamlit UI cost estimate table integration

### User's Domain (Backend/ML)
- Step 2-3: Dataset collection, labeling, YOLOv8 training
- Step 4: FastAPI backend (`/upload`, `/infer`, `/estimate`, `/report`)
- Step 7-8: User edits, VIN decode, GPT summary
- Backend integration and ML inference

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Git

### Setup
1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Development Workflow

We follow a strict **Plan → Implement → Test** cycle for all features:

1. **Plan**: Discuss feature ideas, create detailed plan document in `docs/plans/`
2. **Implement**: Develop the feature according to the plan
3. **Test**: Comprehensive testing from user perspective (frontend + backend)

All plans are stored in `docs/plans/` following the `PLAN_TEMPLATE.md` format.

## 📚 Documentation

- **Project Plan**: `docs/auto_damage_ai_project_plan.md`
- **Development Context**: `docs/DEVELOPMENT_CONTEXT.md`
- **Feature Plans**: `docs/plans/`

## 📅 Timeline

Targeting MVP demo by November with phases from September through mid-November.

## 💰 Estimated MVP Costs

All components use free tiers:
- Model Training: Kaggle/Colab (free tier) - $0
- Backend Hosting: Render/Railway (free tier) - $0
- Frontend: Streamlit Cloud (free tier) - $0
- Database/Storage: Supabase (free tier) - $0
- VIN Decode: NHTSA API (free) - $0
- GPT Summary (optional): ~$0.06–$0.10/month

**Total: <$1/month**

## 📝 License

[To be determined]

---

**Status**: Initial setup phase - File structure and documentation in progress

