# Data Directory

- `auto_damage_repair_costs_MASTER.csv` – CSV rules used by the cost engine.
- `samples/images/Car damages 102.jpg` & `Car damages 201.jpg` – lightweight fixtures used by integration tests.

Full training datasets (Supervisely archive + YOLO exports) are intentionally not stored in this repo. Regenerate them by following the instructions in `tools/label_fusion/README.md` (convert dataset → match damage → build YOLO dataset). Place the processed results under `data/datasets/…` locally if you need to retrain.***
