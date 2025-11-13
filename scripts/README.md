# Helper Scripts

- `run_backend.py` – stops any running FastAPI instance and launches `uvicorn apps.api.main:app --reload`.
- `run_frontend.py` – stops the Vite dev server (if running) and launches `pnpm dev` in `apps/web`.

Usage:
```bash
python scripts/run_backend.py
python scripts/run_frontend.py
```

These scripts are optional; you can always run `uvicorn` / `pnpm dev` directly if you prefer.***
