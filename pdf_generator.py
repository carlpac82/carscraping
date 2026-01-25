"""Modern PDF generator for vehicle inspections"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas as pdf_canvas
import io
import os
import json
import logging
import base64
from PIL import Image
from reportlab.lib.utils import ImageReader

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
    
    # Blue header bar (teal/cyan color like in image)
    header_color = HexColor('#0891b2')
    c.setFillColor(header_color)
    c.rect(0, height - 70, width, 70, fill=1, stroke=0)
    
    # Logo (ap-heather.png)
    logo_path = '/Users/filipepacheco/CascadeProjects/carscraping/static/ap-heather.png'
    if os.path.exists(logo_path):
        try:
            c.drawImage(logo_path, 30, height - 60, width=100, height=40, preserveAspectRatio=True, mask='auto')
        except Exception as e:
            logging.warning(f"Could not load logo: {e}")
    
    # Title in header (white text)
    c.setFillColor(HexColor('#ffffff'))
    c.setFont("Helvetica-Bold", 16)
    
    if inspection_data['inspection_type'] == 'checkin':
        title = "Relatório de Entrega - "
    elif inspection_data['inspection_type'] == 'self_checkout':
        title = "Relatório de Devolução - "
    else:
        title = "Relatório de Devolução - "
    
    title += inspection_data.get('vehicle_plate', 'N/A')
    c.drawString(width / 2 - c.stringWidth(title, "Helvetica-Bold", 16) / 2, height - 40, title)
    
    # Start content
    y_pos = height - 100
    
    # Vehicle and contract info in 2 columns
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(HexColor('#1f2937'))
    
    # Left column
    c.drawString(40, y_pos, "Marca")
    c.setFont("Helvetica", 11)
    c.setFillColor(HexColor('#4b5563'))
    brand = extracted.get('brand', 'N/A')
    c.drawString(40, y_pos - 15, brand)
    
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(HexColor('#1f2937'))
    c.drawString(40, y_pos - 40, "Modelo")
    c.setFont("Helvetica", 11)
    c.setFillColor(HexColor('#4b5563'))
    model = extracted.get('model', 'N/A')
    c.drawString(40, y_pos - 55, model)
    
    # Middle column
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(HexColor('#1f2937'))
    c.drawString(220, y_pos, "Matrícula")
    c.setFont("Helvetica", 11)
    c.setFillColor(HexColor('#4b5563'))
    c.drawString(220, y_pos - 15, inspection_data.get('vehicle_plate', 'N/A'))
    
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(HexColor('#1f2937'))
    c.drawString(220, y_pos - 40, "Cliente")
    c.setFont("Helvetica", 11)
    c.setFillColor(HexColor('#4b5563'))
    client_name = inspection_data.get('client_name') or extracted.get('clientName', 'N/A')
    c.drawString(220, y_pos - 55, client_name)
    
    # Right column
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(HexColor('#1f2937'))
    c.drawString(400, y_pos, "Contrato (RA)")
    c.setFont("Helvetica", 11)
    c.setFillColor(HexColor('#4b5563'))
    c.drawString(400, y_pos - 15, inspection_data['contract_number'])
    
    y_pos -= 85
    
    # Divider
    c.setStrokeColor(HexColor('#e5e7eb'))
    c.line(40, y_pos, width - 40, y_pos)
    y_pos -= 25
    
    # Inspection summary section
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(HexColor('#1f2937'))
    c.drawString(40, y_pos, "Resumo da Inspeção")
    y_pos -= 30
    
    # Two boxes side by side
    box_width = (width - 100) / 2
    box_height = 120
    
    # Left box - Check-in info
    if inspection_data['inspection_type'] == 'checkin':
        box_color = HexColor('#dbeafe')
    else:
        box_color = HexColor('#fef3c7')
    
    c.setFillColor(box_color)
    c.rect(40, y_pos - box_height, box_width, box_height, fill=1, stroke=0)
    
    # Border
    if inspection_data['inspection_type'] == 'checkin':
        border_color = HexColor('#3b82f6')
    else:
        border_color = HexColor('#f59e0b')
    c.setStrokeColor(border_color)
    c.setLineWidth(2)
    c.rect(40, y_pos - box_height, box_width, box_height, fill=0, stroke=1)
    
    # Content
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(HexColor('#1f2937'))
    if inspection_data['inspection_type'] == 'checkin':
        c.drawString(50, y_pos - 25, "Entrega (Check-In)")
    else:
        c.drawString(50, y_pos - 25, "Recolha (Check-Out) - Prevista")
    
    c.setFont("Helvetica", 10)
    c.setFillColor(HexColor('#4b5563'))
    c.drawString(50, y_pos - 45, "Data:")
    date_str = inspection_data['created_at'].strftime('%d/%m/%Y %H:%M') if inspection_data.get('created_at') else 'N/A'
    c.drawString(50, y_pos - 60, date_str)
    
    c.drawString(50, y_pos - 80, "Estado:")
    if inspection_data['inspection_type'] == 'checkin':
        c.setFillColor(HexColor('#10b981'))
        c.drawString(50, y_pos - 95, "Pendente")
    else:
        c.setFillColor(HexColor('#f59e0b'))
        c.drawString(50, y_pos - 95, "Pendente")
    
    # Right box - Return date
    if inspection_data['inspection_type'] == 'checkin':
        box_color = HexColor('#fef3c7')
        c.setFillColor(box_color)
        c.rect(50 + box_width, y_pos - box_height, box_width, box_height, fill=1, stroke=0)
        
        c.setStrokeColor(HexColor('#f59e0b'))
        c.setLineWidth(2)
        c.rect(50 + box_width, y_pos - box_height, box_width, box_height, fill=0, stroke=1)
        
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(HexColor('#1f2937'))
        c.drawString(60 + box_width, y_pos - 25, "Recolha (Check-Out) - Prevista")
        
        c.setFont("Helvetica", 10)
        c.setFillColor(HexColor('#4b5563'))
        c.drawString(60 + box_width, y_pos - 45, "Data:")
        return_date = extracted.get('returnDate') or extracted.get('return_date', 'N/A')
        c.drawString(60 + box_width, y_pos - 60, return_date)
        
        c.drawString(60 + box_width, y_pos - 80, "Estado:")
        c.setFillColor(HexColor('#f59e0b'))
        c.drawString(60 + box_width, y_pos - 95, "Pendente")
    
    y_pos -= box_height + 30
    
    # Croqui de Danos (white background)
    if inspection_data.get('damage_croqui'):
        if y_pos < 250:
            c.showPage()
            y_pos = height - 60
        
        c.setFont("Helvetica-Bold", 13)
        c.setFillColor(HexColor('#1f2937'))
        c.drawString(40, y_pos, "Croqui de Danos")
        y_pos -= 20
        
        try:
            croqui_data = inspection_data['damage_croqui']
            if croqui_data.startswith('data:image'):
                croqui_data = croqui_data.split(',')[1]
            
            img_data = base64.b64decode(croqui_data)
            img = Image.open(io.BytesIO(img_data))
            
            # Convert to RGB if needed and ensure white background
            if img.mode == 'RGBA':
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            img_width = width - 80
            img_height = img_width * img.height / img.width
            
            if img_height > 200:
                img_height = 200
                img_width = img_height * img.width / img.height
            
            # Draw white background box
            c.setFillColor(HexColor('#ffffff'))
            c.rect(40, y_pos - img_height - 10, img_width, img_height + 10, fill=1, stroke=0)
            
            # Draw croqui
            c.drawImage(ImageReader(img), 40, y_pos - img_height, width=img_width, height=img_height)
            
            y_pos -= img_height + 20
        except Exception as e:
            logging.error(f"Error adding croqui to PDF: {e}")
    
    # Photos grid (3x3)
    photos = inspection_data.get('photos', [])
    if photos:
        if y_pos < 400:
            c.showPage()
            y_pos = height - 60
        
        c.setFont("Helvetica-Bold", 13)
        c.setFillColor(HexColor('#1f2937'))
        c.drawString(40, y_pos, "Fotografias da Inspeção")
        y_pos -= 30
        
        # Grid settings
        cols = 3
        photo_size = (width - 100) / cols
        spacing = 10
        
        x_start = 40
        y_start = y_pos
        
        for idx, photo in enumerate(photos[:9]):
            if idx > 0 and idx % cols == 0:
                y_start -= photo_size + spacing
                if y_start < 100:
                    c.showPage()
                    y_start = height - 60
            
            col = idx % cols
            x = x_start + col * (photo_size + spacing)
            y = y_start - photo_size
            
            try:
                photo_data = photo['image_data']
                if photo_data.startswith('data:image'):
                    photo_data = photo_data.split(',')[1]
                
                img_data = base64.b64decode(photo_data)
                img = Image.open(io.BytesIO(img_data))
                
                # Draw photo
                c.drawImage(ImageReader(img), x, y, width=photo_size, height=photo_size, preserveAspectRatio=True)
            except Exception as e:
                logging.error(f"Error adding photo {idx} to PDF: {e}")
    
    # Footer
    c.setFont("Helvetica", 8)
    c.setFillColor(HexColor('#9ca3af'))
    c.drawCentredString(width / 2, 30, "Auto Prudente - Rent a Car")
    
    c.save()
    buffer.seek(0)
    return buffer.getvalue()
