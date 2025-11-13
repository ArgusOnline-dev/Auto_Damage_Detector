# Frontend Polish – Implementation Notes

**Date:** 2025-02-XX  
**Status:** ✅ Completed

## Changes Implemented
1. **Image overlay cleanup**
   - Bounding boxes are now filtered per selected image (`fileId`) and scale dynamically using the image’s natural dimensions, eliminating overflow/off-screen boxes.
   - Boxes only render for damaged parts when “Show intact parts” is off (default). Classes are color-coded by severity (minor = yellow, moderate = orange, severe = red) with labels showing severity.
2. **Detection management**
   - We capture `imageId` + confidence for every detection so the table/overlay know which image they belong to.
   - File picker now highlights the active image; removing files adjusts selection automatically.
3. **Live estimate recalculation**
   - Editing severity or labor hours triggers `/estimate` with the updated detections, so totals respond immediately.
   - Labor rate & parts-preference changes still refresh totals; OEM vs used toggle already wired in.

## Optional Follow-ups
- Highlight table rows belonging to the selected image.
- Formal UI/unit tests + screenshot diffs once the UX is frozen.
