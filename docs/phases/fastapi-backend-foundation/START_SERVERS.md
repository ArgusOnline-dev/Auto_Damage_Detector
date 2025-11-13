# How to Start the Application

## Overview

The Auto Damage Detector application consists of two servers:
1. **Backend (FastAPI)** - Runs on port 8000
2. **Frontend (Vite/React)** - Runs on port 8080

## How It Works

### Architecture

```
┌─────────────────┐         ┌─────────────────┐
│   Frontend      │         │    Backend      │
│   (Port 8080)   │────────▶│   (Port 8000)   │
│   React/Vite    │  Proxy  │   FastAPI       │
└─────────────────┘         └─────────────────┘
```

**How the connection works:**
1. Frontend runs on `http://localhost:8080`
2. Backend runs on `http://localhost:8000`
3. Vite proxy forwards all `/api/*` requests to the backend
4. When frontend calls `/api/v1/upload`, it goes to `http://localhost:8000/api/v1/upload`

### API Flow

1. **User uploads images** → Frontend calls `uploadImages(files)`
   - Sends files to `/api/v1/upload` (proxied to backend)
   - Backend stores files and returns file IDs

2. **User clicks "Analyze"** → Frontend calls `runInference(fileIds)`
   - Sends file IDs to `/api/v1/infer` (proxied to backend)
   - Backend runs ML inference (mock for now) and returns detections

3. **Frontend gets estimate** → Calls `getEstimate(detections, laborRate, useOemParts)`
   - Sends detections to `/api/v1/estimate` (proxied to backend)
   - Backend calculates costs and returns estimate

4. **User downloads PDF** → Frontend calls `downloadPDFReport(reportData)`
   - Sends report data to `/api/v1/report/pdf` (proxied to backend)
   - Backend generates PDF and returns it

## Starting the Servers

### Option 1: Start Both Servers (Recommended)

```bash
python run_all.py
```

This starts both backend and frontend servers automatically.

### Option 2: Start Servers Separately

**Terminal 1 - Backend:**
```bash
python run.py
```

**Terminal 2 - Frontend:**
```bash
cd apps/web
npm install  # First time only
npm run dev
```

Or use the helper script:
```bash
python scripts/run_frontend.py
```

## Access Points

- **Frontend UI**: http://localhost:8080
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

## First Time Setup

### Backend Dependencies
```bash
pip install -r requirements.txt
```

### Frontend Dependencies
```bash
cd apps/web
npm install
```

## Troubleshooting

### Frontend can't connect to backend
- Make sure backend is running on port 8000
- Check that Vite proxy is configured correctly in `apps/web/vite.config.ts`
- Verify CORS is enabled in backend (it is by default)

### Port already in use
- Backend: Change port in `run.py` (default: 8000)
- Frontend: Change port in `apps/web/vite.config.ts` (default: 8080)

### API calls failing
- Check browser console for errors
- Verify backend is running: http://localhost:8000/api/v1/health
- Check network tab in browser dev tools to see API requests

## Development Workflow

1. Start backend: `python run.py`
2. Start frontend: `cd apps/web && npm run dev`
3. Open browser: http://localhost:8080
4. Test the upload → analyze → estimate → PDF workflow
5. Check backend logs for API calls
6. Check browser console for frontend errors

