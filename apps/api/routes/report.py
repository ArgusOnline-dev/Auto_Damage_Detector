"""Report routes for report generation."""
import uuid
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from apps.api.models.report import ReportData, ReportPDFRequest
from apps.api.utils.pdf_generator import generate_pdf
from apps.api.core.exceptions import ReportGenerationError

router = APIRouter(prefix="/report", tags=["report"])

# In-memory report storage (will be replaced with database in future)
_reports = {}


@router.get("/{report_id}", response_model=ReportData, status_code=200)
async def get_report(report_id: str):
    """
    Get estimate report by ID.
    
    Returns full report data including detections and cost estimate.
    """
    if report_id not in _reports:
        raise HTTPException(status_code=404, detail=f"Report not found: {report_id}")
    
    return _reports[report_id]


@router.post("/pdf", status_code=200)
async def generate_report_pdf(request: ReportPDFRequest):
    """
    Generate PDF report.
    
    Accepts report data and returns PDF file.
    """
    try:
        # Store report data (for future retrieval)
        report_id = request.report_data.report_id
        _reports[report_id] = request.report_data
        
        # Generate PDF
        pdf_buffer = generate_pdf(request.report_data)
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=report_{report_id}.pdf"}
        )
    except ReportGenerationError as e:
        raise HTTPException(status_code=500, detail=str(e.detail))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

