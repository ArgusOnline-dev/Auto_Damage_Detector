# Frontend Testing Guide - Backend Integration Polish

This guide explains how to test the new backend features in the frontend UI.

## Prerequisites

1. **Backend server running:**
   ```bash
   cd Auto_Damage_Detector
   python run.py
   ```
   Backend should be available at `http://localhost:8000`

2. **Frontend server running:**
   ```bash
   cd Auto_Damage_Detector
   python scripts/run_frontend.py
   ```
   Frontend should be available at `http://localhost:8080`

## Features to Test

### 1. Multi-Image Upload & Processing

**Steps:**
1. Open the frontend at `http://localhost:8080`
2. Upload **2 or more images** at once (drag & drop or click to select)
3. Click "Analyze Images"

**Expected Results:**
- All images upload successfully
- Analysis processes all images
- Detections from all images are combined and displayed
- Console shows: `Total detections across X image(s): Y`

**What to Check:**
- ✅ Multiple images appear in the "Uploaded Files" list
- ✅ Analysis completes without errors
- ✅ Detection table shows detections from all images
- ✅ Cost estimate includes all detections

### 2. Intact Parts Filtering

**Steps:**
1. Upload 1-2 images with car damage
2. **Before clicking "Analyze Images":**
   - Check/uncheck the "Show intact parts" checkbox
3. Click "Analyze Images"

**Test Case A: Show Intact Parts = OFF (default)**
- **Expected:** Only damaged parts are shown (dent, scratch, cracked, etc.)
- **Check:** Detection table should NOT show parts with "intact" damage type
- **Console:** Should show `Filtered out X intact detections`

**Test Case B: Show Intact Parts = ON**
- **Expected:** All parts are shown, including intact ones
- **Check:** Detection table should show parts with "intact" damage type
- **Console:** Should show `filtered_count=0`

**What to Check:**
- ✅ Toggle works correctly
- ✅ When OFF: Only damaged parts appear
- ✅ When ON: All parts appear (including intact)
- ✅ Console logs show filtered_count when intact parts are hidden
- ✅ Cost estimate only includes visible detections

### 3. Empty Detection Handling

**Steps:**
1. Upload an image where all parts are intact
2. Make sure "Show intact parts" is **OFF**
3. Click "Analyze Images"

**Expected Results:**
- Toast notification appears: "No damaged parts detected. All parts appear intact."
- Suggests enabling "Show Intact Parts" to see all detections
- Detection table is empty
- Cost estimate section is hidden

**What to Check:**
- ✅ Helpful error message appears
- ✅ UI handles empty state gracefully
- ✅ No crashes or errors in console

### 4. Two-Stage Model Verification

**Steps:**
1. Upload an image with visible damage
2. Analyze with "Show intact parts" = OFF
3. Check the detection table

**Expected Results:**
- Parts show clean names: `front_door`, `bumper`, `headlight` (NOT `door_broken_part`)
- Damage types are separate: `dent`, `scratch`, `cracked`, `broken_part`, etc.
- Each detection has both `part` and `damage_type` fields

**What to Check:**
- ✅ Part names are clean (no combined labels)
- ✅ Damage types are separate fields
- ✅ Console shows proper structure: `part=front_door damage=dent`

### 5. Cost Estimation with Filtered Detections

**Steps:**
1. Upload images
2. Analyze with "Show intact parts" = OFF
3. Check the cost estimate table

**Expected Results:**
- Line items only include damaged parts (no intact parts)
- Totals reflect only damaged parts
- Changing labor rate or parts preference updates estimate correctly

**What to Check:**
- ✅ Cost table matches visible detections
- ✅ No intact parts in cost calculation
- ✅ Estimate updates when settings change

## Console Logging

Open browser DevTools (F12) → Console tab to see detailed logs:

**Expected Console Output:**
```
Uploading images... 2
Uploaded file IDs: ["uuid1", "uuid2"]
Running inference... ["uuid1", "uuid2"] includeIntact: false
Inference result: {results: [...], include_intact: false, filtered_count: 35}
Total detections across 2 image(s): 2
Filtered out 35 intact detections
Getting estimate... 2 detections
Estimate result: {line_items: [...], totals: {...}}
```

## Troubleshooting

**Issue: "No detections found"**
- Check if "Show intact parts" is enabled
- Verify images contain visible car parts
- Check browser console for API errors

**Issue: Detections show combined labels (e.g., "door_broken_part")**
- Backend may be using wrong model
- Check `.env` file: `PART_MODEL_PATH=models/yolov8n_part_detector.pt`
- Restart backend server

**Issue: Frontend shows old API response format**
- Clear browser cache
- Restart frontend dev server
- Check that `apps/web/src/lib/api.ts` has updated `InferenceResponse` interface

## Success Criteria

✅ Multi-image upload works  
✅ Intact filtering toggle works correctly  
✅ Empty detections handled gracefully  
✅ Clean part names (not combined labels)  
✅ Cost estimation works with filtered detections  
✅ Console shows proper logging  
✅ No errors in browser console or backend logs

