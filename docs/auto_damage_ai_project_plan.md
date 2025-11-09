# 🚗 AI-Powered Auto Damage Estimator — Project Plan

## 🧩 Overview
This project aims to build an AI-powered web application that detects car damages from uploaded photos and generates a transparent repair cost estimate.  
The MVP focuses on consumers and small businesses (mechanic shops, towing companies, rental fleets), emphasizing **transparency, explainability, and affordability**.

---

## ⚙️ Features

| Feature | Description |
|----------|--------------|
| **Upload** | Users can upload multiple car photos (front, sides, rear). |
| **Detection** | YOLOv8 model detects 10–12 key parts and labels damage type (dent, scrape, crack, missing, intact). |
| **Severity** | Damage severity bucketed into minor, moderate, or severe using rules. |
| **Cost Engine** | CSV-driven rules: labor hours × labor rate, parts costs (new/used ranges), paint/material adders. |
| **Report** | Line-item estimate with totals (min/likely/max). Export as PDF. |
| **Explainability** | Transparent mapping from detection → severity → cost rules. Optional GPT summary for human-readable report. |
| **User Input** | Users can set labor rate, toggle OEM/Used parts, and edit severity for accuracy. |

---

## 🧠 Dataset Information

- **Kaggle Datasets:** Car Damage Detection, Car Parts Segmentation (free, CC licenses)
- **Roboflow Universe:** Vehicle damage and parts datasets in YOLOv8 format (free tier)
- **Custom Labels:** 200–300 manually labeled images for missing parts & severity cases
- **Data Format:** YOLOv8-ready (`images/` + `labels/` folders + `data.yaml`)

---

## 🪜 Step-by-Step Plan

| Step | Action |
|------|---------|
| 1 | Define scope (parts, damage states, severity rules). Create `cost_rules.csv` with public labor/parts costs. |
| 2 | Assemble datasets from Kaggle/Roboflow. Label 200–300 custom images in YOLOv8 format. |
| 3 | Train YOLOv8n (Colab/Kaggle GPU). Evaluate on hold-out set (mAP > 0.6). |
| 4 | Build **FastAPI backend**: `/upload`, `/infer`, `/estimate`, `/report`. |
| 5 | Develop **Streamlit UI**: upload → detection gallery → cost estimate table → PDF export. |
| 6 | Integrate severity scoring + cost engine (CSV-driven). |
| 7 | Add user edits (severity dropdown, OEM/Used toggle). |
| 8 | Add VIN decode (NHTSA API) and optional GPT summary. |
| 9 | Testing: Run 10–20 cars, compare system vs. manual estimates. |
| 10 | Finalize MVP demo by November with working app + example reports. |

---

## 📆 Timeline (to November)

| Phase | Weeks | Milestones |
|--------|--------|-------------|
| **September (Weeks 1–2)** | Scope, cost_rules.csv, dataset collection & labeling |
| **October (Weeks 3–6)** | Train YOLOv8, build backend APIs, Streamlit UI skeleton |
| **Late October (Weeks 7–8)** | Integrate cost engine, severity rules, editing features |
| **Early November (Week 9)** | Add VIN decode, GPT summary, polish UI |
| **Mid-November (Week 10)** | Testing + Demo prep with sample reports |

---

## 💰 Estimated MVP Costs

| Component | Source | Cost |
|------------|----------|------|
| **Model Training** | Kaggle/Colab (free tier) | $0 |
| **Datasets** | Kaggle + Roboflow public | $0 |
| **Backend Hosting** | Render/Railway (free tier ~750–1000h/month) | $0 |
| **Frontend** | Streamlit Cloud (free tier) | $0 |
| **Database/Storage** | Supabase (≤500MB, 50k requests) | $0 |
| **VIN Decode** | NHTSA API (free) | $0 |
| **PDF Generation** | ReportLab (open-source) | $0 |
| **GPT Summary (optional)** | gpt-4o-mini (~$0.0003/request) | ~$0.06–$0.10/month |
| **Total** | | **<$1/month** |

Reports supported: 100–200 per month within free-tier limits.

---

*Converted automatically from PDF for Cursor readability.*