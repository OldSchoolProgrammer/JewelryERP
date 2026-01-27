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
        bottomMargin=120 # Increased to reserve space for bottom signature
    )
    
    styles = getSampleStyleSheet()
    
    # Brand Colors
    BRAND_BG = colors.HexColor('#120b00')
    BRAND_TEXT = colors.HexColor('#FFE100')
    
    michaello_style = ParagraphStyle(
        'Michaello',
        parent=styles['Normal'],
        fontSize=28,
        alignment=TA_CENTER,
        textColor=BRAND_TEXT,
        fontName='Helvetica-Bold',
        leading=30,
    )
    
    jewellery_style = ParagraphStyle(
        'Jewellery',
        parent=styles['Normal'],
        fontSize=16,
        alignment=TA_CENTER,
        textColor=BRAND_TEXT,
        fontName='Courier',
        leading=18,
    )
    
    cert_title_style = ParagraphStyle(
        'CertTitle',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_CENTER,
        textColor=colors.grey,
        spaceAfter=5,
    )
    
    cert_number_style = ParagraphStyle(
        'CertNumber',
        parent=styles['Normal'],
        fontSize=22,
        alignment=TA_CENTER,
        spaceAfter=15,
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
        spaceAfter=15,
    )
    
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_CENTER,
        textColor=colors.grey,
        leading=16,
    )
    
    elements = []
    
    # Logo Header Section
    logo_data = [
        [Paragraph("Michaello", michaello_style)],
        [Paragraph("JEWELLERY", jewellery_style)]
    ]
    logo_table = Table(logo_data, colWidths=[6.5*inch])
    logo_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BRAND_BG),
        ('TOPPADDING', (0, 0), (-1, 0), 15),
        ('BOTTOMPADDING', (0, 1), (-1, 1), 15),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    elements.append(logo_table)
    elements.append(Spacer(1, 20))
    
    # Title & Certificate Number
    elements.append(Paragraph("CERTIFICATE OF AUTHENTICITY", cert_title_style))
    elements.append(Paragraph(certificate.certificate_number, cert_number_style))
    
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
        ('BACKGROUND', (0, 0), (-1, 0), BRAND_BG),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
        ('SPAN', (0, 0), (-1, 0)),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 15))
    
    # Issue Date
    elements.append(Paragraph(
        f"Issue Date: {certificate.issued_at.strftime('%B %d, %Y')}",
        center_style
    ))
    
    elements.append(Spacer(1, 20))
    
    # Footer
    footer_text = """
    Michaello Jewellery, certifies that every component of this jewel is genuine and of good quality 
    per the details provided hereby, according to the standards of the International Gemological Institute.
    """
    elements.append(Paragraph(footer_text, footer_style))
    
    # Define a function to draw the signature at the bottom of the page
    def draw_fixed_elements(canvas, doc):
        canvas.saveState()
        
        # Signature section coordinates (from bottom)
        sig_y_text = 40
        sig_y_line = 55
        sig_y_img = 60
        
        # Draw Authorized Signature text
        canvas.setFont("Helvetica", 10)
        canvas.setFillColor(colors.grey)
        canvas.drawCentredString(letter[0]/2, sig_y_text, "Authorized Signature")
        
        # Draw line
        canvas.setStrokeColor(colors.black)
        canvas.setLineWidth(0.5)
        canvas.line(letter[0]/2 - 100, sig_y_line, letter[0]/2 + 100, sig_y_line)
        
        # Draw signature image if it exists
        sig_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'signature.png')
        if os.path.exists(sig_path):
            try:
                canvas.drawImage(sig_path, letter[0]/2 - 65, sig_y_img, width=130, height=60, mask='auto')
            except:
                pass # Fallback if image is corrupted
                
        canvas.restoreState()

    doc.build(elements, onFirstPage=draw_fixed_elements)
    
    # Save to model
    pdf_content = buffer.getvalue()
    buffer.close()
    
    filename = f'{certificate.certificate_number}.pdf'
    certificate.pdf_file.save(filename, ContentFile(pdf_content), save=True)
    
    return certificate.pdf_file
