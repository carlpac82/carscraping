"""Modern PDF generator for vehicle inspections"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas as pdf_canvas
import io
import os
import json
import logging

def generate_inspection_pdf(inspection_data, extracted_data_json):
    """Generate a modern, clean PDF for check-in, check-out, or self-checkout inspection"""
    
    # Parse extracted_data
    extracted = {}
    if extracted_data_json:
        try:
            if isinstance(extracted_data_json, str):
                extracted = json.loads(extracted_data_json)
            else:
                extracted = extracted_data_json
        except:
            pass
    
    # Create PDF
    buffer = io.BytesIO()
    c = pdf_canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Blue header bar
    header_color = HexColor('#1e40af')
    c.setFillColor(header_color)
    c.rect(0, height - 60, width, 60, fill=1, stroke=0)
    
    # Logo
    logo_path = '/Users/filipepacheco/CascadeProjects/carscraping/static/logos/logo_autoprudente_header.png'
    if os.path.exists(logo_path):
        try:
            c.drawImage(logo_path, 20, height - 55, width=120, height=50, preserveAspectRatio=True, mask='auto')
        except Exception as e:
            logging.warning(f"Could not load logo: {e}")
    
    # RA number on right
    c.setFillColor(HexColor('#ffffff'))
    c.setFont("Helvetica-Bold", 14)
    c.drawRightString(width - 20, height - 35, f"RA: {inspection_data['contract_number']}")
    
    # Title
    y_pos = height - 90
    c.setFillColor(HexColor('#1f2937'))
    c.setFont("Helvetica-Bold", 20)
    
    if inspection_data['inspection_type'] == 'checkin':
        title = "Relatório de Entrega (Check-In)"
    elif inspection_data['inspection_type'] == 'self_checkout':
        title = "Relatório de Devolução (Self Check-Out)"
    else:
        title = "Relatório de Devolução (Check-Out)"
    
    c.drawString(40, y_pos, title)
    
    # Inspection details
    y_pos -= 40
    c.setFont("Helvetica", 11)
    c.setFillColor(HexColor('#4b5563'))
    
    details = [
        f"Nº Inspeção: {inspection_data['inspection_number']}",
        f"Data: {inspection_data['created_at'].strftime('%d/%m/%Y às %H:%M') if inspection_data.get('created_at') else 'N/A'}",
        f"Inspetor: {inspection_data.get('inspector_name', 'N/A')}",
    ]
    
    for detail in details:
        c.drawString(40, y_pos, detail)
        y_pos -= 20
    
    # Divider
    y_pos -= 10
    c.setStrokeColor(HexColor('#e5e7eb'))
    c.line(40, y_pos, width - 40, y_pos)
    y_pos -= 30
    
    # Vehicle info
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(HexColor('#1f2937'))
    c.drawString(40, y_pos, "Informação do Veículo")
    y_pos -= 25
    
    c.setFont("Helvetica", 11)
    c.setFillColor(HexColor('#4b5563'))
    
    c.drawString(40, y_pos, f"Matrícula: {inspection_data.get('vehicle_plate', 'N/A')}")
    y_pos -= 20
    c.drawString(40, y_pos, f"Quilómetros: {inspection_data.get('odometer_reading', 'N/A')} km")
    y_pos -= 20
    c.drawString(40, y_pos, f"Combustível: {inspection_data.get('fuel_level', 'N/A')}")
    y_pos -= 30
    
    # Client info
    if inspection_data.get('client_name') or extracted.get('clientName'):
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(HexColor('#1f2937'))
        c.drawString(40, y_pos, "Cliente")
        y_pos -= 25
        
        c.setFont("Helvetica", 11)
        c.setFillColor(HexColor('#4b5563'))
        client_name = inspection_data.get('client_name') or extracted.get('clientName', 'N/A')
        c.drawString(40, y_pos, f"Nome: {client_name}")
        y_pos -= 30
    
    # Rental info
    if extracted:
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(HexColor('#1f2937'))
        c.drawString(40, y_pos, "Aluguer")
        y_pos -= 25
        
        c.setFont("Helvetica", 11)
        c.setFillColor(HexColor('#4b5563'))
        
        if extracted.get('pickupDate'):
            c.drawString(40, y_pos, f"Levantamento: {extracted['pickupDate']}")
            y_pos -= 20
        if extracted.get('returnDate') or extracted.get('return_date'):
            return_date = extracted.get('returnDate') or extracted.get('return_date')
            c.drawString(40, y_pos, f"Devolução Prevista: {return_date}")
            y_pos -= 20
        y_pos -= 10
    
    # Observations
    if inspection_data.get('inspector_notes'):
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(HexColor('#1f2937'))
        c.drawString(40, y_pos, "Observações")
        y_pos -= 25
        
        c.setFont("Helvetica", 10)
        c.setFillColor(HexColor('#4b5563'))
        
        notes = inspection_data['inspector_notes']
        max_width = width - 80
        words = notes.split()
        line = ""
        
        for word in words:
            test_line = line + word + " "
            if c.stringWidth(test_line, "Helvetica", 10) < max_width:
                line = test_line
            else:
                c.drawString(40, y_pos, line.strip())
                y_pos -= 15
                line = word + " "
                if y_pos < 100:
                    c.showPage()
                    y_pos = height - 60
        
        if line:
            c.drawString(40, y_pos, line.strip())
            y_pos -= 20
    
    # Damage croqui
    if inspection_data.get('damage_croqui'):
        y_pos -= 20
        if y_pos < 300:
            c.showPage()
            y_pos = height - 60
        
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(HexColor('#1f2937'))
        c.drawString(40, y_pos, "Croqui de Danos")
        y_pos -= 25
        
        try:
            import base64
            from PIL import Image
            from reportlab.lib.utils import ImageReader
            
            croqui_data = inspection_data['damage_croqui']
            if croqui_data.startswith('data:image'):
                croqui_data = croqui_data.split(',')[1]
            
            img_data = base64.b64decode(croqui_data)
            img = Image.open(io.BytesIO(img_data))
            
            img_width = width - 80
            img_height = img_width * img.height / img.width
            
            if img_height > y_pos - 100:
                img_height = y_pos - 100
                img_width = img_height * img.width / img.height
            
            c.drawImage(ImageReader(img), 40, y_pos - img_height, width=img_width, height=img_height)
        except Exception as e:
            logging.error(f"Error adding croqui to PDF: {e}")
    
    # Footer
    c.setFont("Helvetica", 8)
    c.setFillColor(HexColor('#9ca3af'))
    c.drawCentredString(width / 2, 30, "Auto Prudente - Rent a Car")
    
    c.save()
    buffer.seek(0)
    return buffer.getvalue()
