import os
from io import BytesIO
from django.conf import settings
from django.core.files.base import ContentFile
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER


def generate_certificate_pdf(certificate):
    """Generate a PDF certificate for a jewelry item."""
    buffer = BytesIO()
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=24,
        alignment=TA_CENTER,
        spaceAfter=30,
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=14,
        alignment=TA_CENTER,
        textColor=colors.grey,
        spaceAfter=40,
    )
    
    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
    )
    
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6,
    )
    
    center_style = ParagraphStyle(
        'Center',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_CENTER,
        spaceAfter=20,
    )
    
    elements = []
    
    # Title
    elements.append(Paragraph("CERTIFICATE OF AUTHENTICITY", title_style))
    elements.append(Paragraph("Jewelry Store", subtitle_style))
    
    # Certificate Number
    elements.append(Paragraph(f"Certificate No: {certificate.certificate_number}", center_style))
    elements.append(Spacer(1, 20))
    
    # Item Details
    item = certificate.item
    
    data = [
        ['Item Details', ''],
        ['SKU:', item.sku],
        ['Name:', item.name],
        ['Metal:', item.get_metal_display()],
        ['Purity:', item.purity or 'N/A'],
        ['Weight:', f'{item.weight_grams} grams' if item.weight_grams else 'N/A'],
    ]
    
    if item.stone_details:
        data.append(['Stone Details:', item.stone_details])
    
    if item.category:
        data.append(['Category:', item.category.name])
    
    table = Table(data, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#212529')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
        ('SPAN', (0, 0), (-1, 0)),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 30))
    
    # Issue Date
    elements.append(Paragraph(
        f"Issue Date: {certificate.issued_at.strftime('%B %d, %Y')}",
        center_style
    ))
    
    elements.append(Spacer(1, 40))
    
    # Footer
    footer_text = """
    This certificate confirms the authenticity and specifications of the above jewelry item.
    Please retain this certificate for your records.
    """
    elements.append(Paragraph(footer_text, center_style))
    
    elements.append(Spacer(1, 30))
    
    # Signature line
    sig_data = [
        ['_' * 30, '', '_' * 30],
        ['Authorized Signature', '', 'Date'],
    ]
    sig_table = Table(sig_data, colWidths=[2.5*inch, 1*inch, 2.5*inch])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 1), (-1, 1), colors.grey),
    ]))
    elements.append(sig_table)
    
    doc.build(elements)
    
    # Save to model
    pdf_content = buffer.getvalue()
    buffer.close()
    
    filename = f'certificate_{certificate.certificate_number}.pdf'
    certificate.pdf_file.save(filename, ContentFile(pdf_content), save=True)
    
    return certificate.pdf_file
