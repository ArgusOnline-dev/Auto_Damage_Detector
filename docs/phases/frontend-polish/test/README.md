# Frontend Polish – Test Checklist

Manual smoke tests after starting the frontend (`pnpm dev`) and backend (`uvicorn apps.api.main:app --reload`):

1. **Overlay accuracy**
   - Upload at least two images.
   - Switch between thumbnails; confirm only detections for the selected image appear and boxes align with damaged panels (no overflow).
   - Toggle “Show intact parts” on/off and verify boxes/table entries update.

2. **Severity & labor edits**
   - Change severity from Moderate → Minor and click outside the select; totals in the “Cost Estimate” card should update automatically.
   - Edit labor hours (e.g., change 8.0 to 4.0) and confirm totals recalc.

3. **OEM/Used toggle**
   - Switch between OEM / Used / Both; likely total should decrease when choosing Used.

4. **Multi-image workflow**
   - Ensure PDF generation and “Save Draft” still work after edits.

Record results (pass/fail, screenshots) in this folder when you run the tests.***
