"""PDF report generation utility."""
import uuid
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from apps.api.models.report import ReportData
from apps.api.core.exceptions import ReportGenerationError


def generate_pdf(report_data: ReportData) -> BytesIO:
    """
    Generate PDF report from report data.
    
    Args:
        report_data: ReportData model with all report information
        
    Returns:
        BytesIO object containing PDF bytes
    """
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30
        )
        story.append(Paragraph("Auto Damage Repair Estimate", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Report ID
        story.append(Paragraph(f"<b>Report ID:</b> {report_data.report_id}", styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
        
        # Settings
        story.append(Paragraph(f"<b>Labor Rate:</b> ${report_data.labor_rate:.2f}/hour", styles['Normal']))
        story.append(Paragraph(
            f"<b>Parts Type:</b> {'OEM' if report_data.use_oem_parts else 'Used'}",
            styles['Normal']
        ))
        story.append(Spacer(1, 0.2*inch))
        
        # Detections Summary
        story.append(Paragraph("<b>Damage Detections</b>", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        
        if report_data.detections:
            detection_data = [["Part", "Damage Type", "Severity", "Confidence"]]
            for det in report_data.detections:
                detection_data.append([
                    det.part,
                    det.damage_type,
                    det.severity or "N/A",
                    f"{det.confidence:.2%}"
                ])
            
            detection_table = Table(detection_data, colWidths=[2*inch, 1.5*inch, 1*inch, 1*inch])
            detection_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(detection_table)
        else:
            story.append(Paragraph("No detections found.", styles['Normal']))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Cost Estimate
        story.append(Paragraph("<b>Cost Estimate</b>", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        
        if report_data.line_items:
            cost_data = [["Part", "Damage", "Severity", "Labor Hours", "Labor Cost", "Part Cost", "Total"]]
            for item in report_data.line_items:
                part_cost = item.part_cost_new if report_data.use_oem_parts else item.part_cost_used
                total_cost = item.total_new if report_data.use_oem_parts else item.total_used
                cost_data.append([
                    item.part,
                    item.damage_type,
                    item.severity,
                    f"{item.labor_hours:.1f}",
                    f"${item.labor_cost:.2f}",
                    f"${part_cost:.2f}",
                    f"${total_cost:.2f}"
                ])
            
            cost_table = Table(cost_data, colWidths=[1.2*inch, 1*inch, 0.8*inch, 0.8*inch, 1*inch, 1*inch, 1*inch])
            cost_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(cost_table)
        else:
            story.append(Paragraph("No line items.", styles['Normal']))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Totals
        story.append(Paragraph("<b>Total Estimate</b>", styles['Heading2']))
        totals_data = [
            ["Minimum (Used Parts)", f"${report_data.totals.min:.2f}"],
            ["Likely (OEM Parts)", f"${report_data.totals.likely:.2f}"],
            ["Maximum (with buffer)", f"${report_data.totals.max:.2f}"]
        ]
        totals_table = Table(totals_data, colWidths=[3*inch, 2*inch])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey)
        ]))
        story.append(totals_table)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        raise ReportGenerationError(f"Failed to generate PDF: {str(e)}")

