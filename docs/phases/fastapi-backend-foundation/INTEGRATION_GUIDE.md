# Frontend-Backend Integration Guide

## Quick Start

### Start Both Servers

**Option 1: Start Both Automatically**
```bash
python run_all.py
```

**Option 2: Start Separately (Recommended for Development)**

**Terminal 1 - Backend:**
```bash
python run.py
```
Backend will be available at: http://localhost:8000

**Terminal 2 - Frontend:**
```bash
cd apps/web
npm run dev
```
Frontend will be available at: http://localhost:8080

### Test Integration

```bash
python docs/phases/fastapi-backend-foundation/test/test_integration.py
```

Or from the project root:
```bash
cd docs/phases/fastapi-backend-foundation/test
python test_integration.py
```

This will check if both servers are running and can communicate.

## How It Works

### Architecture

```
┌─────────────────────────────────────────────────┐
│  Browser (http://localhost:8080)                │
│  ┌───────────────────────────────────────────┐  │
│  │  React Frontend (Vite Dev Server)         │  │
│  │  - Upload page                             │  │
│  │  - Reports page                            │  │
│  │  - API calls via /api/*                    │  │
│  └──────────────┬────────────────────────────┘  │
│                 │ Proxy                          │
│                 │ /api → http://localhost:8000  │
└─────────────────┼───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│  FastAPI Backend (http://localhost:8000)        │
│  ┌───────────────────────────────────────────┐  │
│  │  API Endpoints:                           │  │
│  │  - POST /api/v1/upload                    │  │
│  │  - POST /api/v1/infer                      │  │
│  │  - POST /api/v1/estimate                   │  │
│  │  - POST /api/v1/report/pdf                  │  │
│  │  - GET /api/v1/health                      │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

### How Frontend Connects to Backend

1. **Vite Proxy Configuration** (`apps/web/vite.config.ts`):
   ```typescript
   proxy: {
     "/api": {
       target: "http://localhost:8000",
       changeOrigin: true,
     }
   }
   ```
   This forwards all `/api/*` requests from frontend to backend.

2. **API Client** (`apps/web/src/lib/api.ts`):
   - All API calls use `/api/v1/*` paths
   - Vite automatically proxies these to `http://localhost:8000/api/v1/*`
   - No CORS issues because requests go through the proxy

3. **Example Flow**:
   ```
   User clicks "Analyze Images"
   ↓
   Frontend calls: uploadImages(files)
   ↓
   API client sends: POST /api/v1/upload
   ↓
   Vite proxy forwards to: http://localhost:8000/api/v1/upload
   ↓
   FastAPI backend processes request
   ↓
   Response sent back through proxy
   ↓
   Frontend receives file IDs
   ```

## Testing the Integration

### Manual Testing

1. **Start both servers** (see Quick Start above)

2. **Open browser**: http://localhost:8080

3. **Test Upload Flow**:
   - Go to Upload page
   - Upload test images (use test images from `docs/phases/fastapi-backend-foundation/test/`)
   - Click "Analyze Images"
   - Verify detections appear
   - Check cost estimate
   - Download PDF report

4. **Check Browser Console**:
   - Open DevTools (F12)
   - Check Network tab for API calls
   - Verify requests go to `/api/v1/*`
   - Check for any errors

5. **Check Backend Logs**:
   - Look at terminal running `python run.py`
   - Verify API requests are received
   - Check for any errors

### Automated Testing

```bash
python docs/phases/fastapi-backend-foundation/test/test_integration.py
```

This checks:
- ✅ Backend is running
- ✅ Frontend is running
- ✅ API proxy is working

## Troubleshooting

### Frontend can't connect to backend

**Symptoms:**
- API calls fail with network errors
- Browser console shows CORS errors
- 404 errors on API endpoints

**Solutions:**
1. Verify backend is running: http://localhost:8000/api/v1/health
2. Check Vite proxy config in `apps/web/vite.config.ts`
3. Restart both servers
4. Check browser console for specific errors

### Buttons don't work

**Symptoms:**
- Upload button doesn't respond
- Analyze button doesn't work
- No API calls in network tab

**Solutions:**
1. Check browser console for JavaScript errors
2. Verify frontend dependencies are installed: `cd apps/web && npm install --legacy-peer-deps`
3. Check if frontend server is running: http://localhost:8080
4. Verify API client is imported correctly

### API calls return errors

**Symptoms:**
- 422 validation errors
- 500 server errors
- 404 not found errors

**Solutions:**
1. Check backend logs for error details
2. Verify request format matches API contract
3. Check API documentation: http://localhost:8000/docs
4. Test API directly using Swagger UI

## Next Steps

Once integration is working:
1. ✅ Test full workflow: Upload → Analyze → Estimate → PDF
2. ✅ Verify all buttons work
3. ✅ Check error handling
4. ✅ Test with different images
5. ✅ Move on to ML model integration (Step 2-3)

## Files Created

- `scripts/run_frontend.py` - Start frontend server
- `run_all.py` - Start both servers (in project root)
- `test_integration.py` - Test integration (in `docs/phases/fastapi-backend-foundation/test/`)
- `INTEGRATION_GUIDE.md` - This guide (in `docs/phases/fastapi-backend-foundation/`)
- `START_SERVERS.md` - Quick start guide (in `docs/phases/fastapi-backend-foundation/`)

