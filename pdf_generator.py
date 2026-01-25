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
    
    # Cyan header bar
    header_color = HexColor('#009cb6')
    c.setFillColor(header_color)
    c.rect(0, height - 70, width, 70, fill=1, stroke=0)
    
    # Logo on left (ap-heather.png)
    logo_path = '/Users/filipepacheco/CascadeProjects/carscraping/static/ap-heather.png'
    if os.path.exists(logo_path):
        try:
            c.drawImage(logo_path, 30, height - 60, width=150, height=50, preserveAspectRatio=True, mask='auto')
        except Exception as e:
            logging.warning(f"Could not load logo: {e}")
    
    # RA number on right in header (white text in box)
    c.setFillColor(HexColor('#ffffff'))
    c.setFont("Helvetica-Bold", 18)
    ra_text = f"R.A.: {inspection_data['contract_number']}"
    ra_width = c.stringWidth(ra_text, "Helvetica-Bold", 18)
    
    # Box for RA
    box_padding = 15
    box_x = width - ra_width - box_padding * 2 - 30
    box_y = height - 55
    c.setFillColor(HexColor('#ffffff'))
    c.setFillColorRGB(1, 1, 1, alpha=0.2)
    c.roundRect(box_x, box_y, ra_width + box_padding * 2, 30, 5, fill=1, stroke=0)
    
    c.setFillColor(HexColor('#ffffff'))
    c.drawString(box_x + box_padding, box_y + 8, ra_text)
    
    # Start content - Title below header
    y_pos = height - 90
    
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(HexColor('#1f2937'))
    
    if inspection_data['inspection_type'] == 'checkin':
        title = "Relatório de Entrega - "
    elif inspection_data['inspection_type'] == 'self_checkout':
        title = "Relatório de Devolução - "
    else:
        title = "Relatório de Devolução - "
    
    title += inspection_data.get('vehicle_plate', 'N/A')
    c.drawCentredString(width / 2, y_pos, title)
    
    y_pos -= 30
    
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
    
    # Helper function to convert fuel level to percentage
    def fuel_to_percent(fuel_level):
        fuel_map = {'R': 0, '1/8': 12.5, '1/4': 25, '3/8': 37.5, '1/2': 50, '5/8': 62.5, '3/4': 75, '7/8': 87.5, 'F': 100}
        return fuel_map.get(fuel_level, 0)
    
    # Inspection summary section
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(HexColor('#1f2937'))
    c.drawString(40, y_pos, "Resumo da Inspeção")
    y_pos -= 30
    
    # Two boxes side by side
    box_width = (width - 100) / 2
    box_height = 180
    
    # Left box - Check-in info (GREEN like in history)
    if inspection_data['inspection_type'] == 'checkin':
        box_color = HexColor('#ecfdf5')  # bg-green-50
        border_color = HexColor('#10b981')  # border-green-500
        title_color = HexColor('#047857')  # text-green-700
    else:
        box_color = HexColor('#dbeafe')  # bg-blue-50
        border_color = HexColor('#3b82f6')  # border-blue-500
        title_color = HexColor('#1e40af')  # text-blue-700
    
    c.setFillColor(box_color)
    c.rect(40, y_pos - box_height, box_width, box_height, fill=1, stroke=0)
    
    c.setStrokeColor(border_color)
    c.setLineWidth(1)
    c.rect(40, y_pos - box_height, box_width, box_height, fill=0, stroke=1)
    
    # Content
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(title_color)
    if inspection_data['inspection_type'] == 'checkin':
        c.drawString(50, y_pos - 25, "Entrega (Check-In)")
    else:
        c.drawString(50, y_pos - 25, "Recolha (Check-Out)")
    
    c.setFont("Helvetica", 9)
    c.setFillColor(HexColor('#4b5563'))
    c.drawString(50, y_pos - 45, "Data:")
    c.setFont("Helvetica-Bold", 9)
    date_str = inspection_data['created_at'].strftime('%d/%m/%Y %H:%M') if inspection_data.get('created_at') else 'N/A'
    c.drawString(120, y_pos - 45, date_str)
    
    c.setFont("Helvetica", 9)
    c.setFillColor(HexColor('#4b5563'))
    if inspection_data['inspection_type'] == 'checkin':
        c.drawString(50, y_pos - 60, "Entregue por:")
    else:
        c.drawString(50, y_pos - 60, "Recolhido por:")
    c.setFont("Helvetica-Bold", 9)
    c.drawString(120, y_pos - 60, inspection_data.get('inspector_name', 'N/A'))
    
    c.setFont("Helvetica", 9)
    c.setFillColor(HexColor('#4b5563'))
    c.drawString(50, y_pos - 75, "Quilómetros:")
    c.setFont("Helvetica-Bold", 9)
    odometer = inspection_data.get('odometer_reading', 'N/A')
    c.drawString(120, y_pos - 75, f"{odometer} km" if odometer != 'N/A' else 'N/A')
    
    # Fuel bar (like in history)
    fuel_level = inspection_data.get('fuel_level', 'R')
    fuel_percent = fuel_to_percent(fuel_level)
    
    # Divider line
    c.setStrokeColor(border_color)
    c.setLineWidth(0.5)
    c.line(50, y_pos - 95, 40 + box_width - 10, y_pos - 95)
    
    c.setFont("Helvetica", 8)
    c.setFillColor(HexColor('#4b5563'))
    label_text = "Combustível na Entrega" if inspection_data['inspection_type'] == 'checkin' else "Combustível na Recolha"
    c.drawCentredString(40 + box_width / 2, y_pos - 110, label_text)
    
    # Fuel markers (R, 1/4, 1/2, 3/4, F)
    marker_y = y_pos - 125
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(HexColor('#009cb6'))
    bar_left = 50
    bar_width_inner = box_width - 20
    c.drawString(bar_left, marker_y, "R")
    c.drawString(bar_left + bar_width_inner * 0.25 - 5, marker_y, "1/4")
    c.drawString(bar_left + bar_width_inner * 0.5 - 5, marker_y, "1/2")
    c.drawString(bar_left + bar_width_inner * 0.75 - 5, marker_y, "3/4")
    c.drawString(bar_left + bar_width_inner - 5, marker_y, "F")
    
    # Fuel bar background
    bar_y = y_pos - 145
    c.setStrokeColor(HexColor('#009cb6'))
    c.setLineWidth(2)
    c.setFillColor(HexColor('#ffffff'))
    c.rect(bar_left, bar_y, bar_width_inner, 15, fill=1, stroke=1)
    
    # Fuel bar markers (vertical lines)
    c.setStrokeColor(HexColor('#009cb6'))
    c.setLineWidth(0.5)
    for pos in [0, 0.25, 0.5, 0.75, 1.0]:
        x = bar_left + bar_width_inner * pos
        c.line(x, bar_y + 5, x, bar_y + 10)
    
    # Fuel bar fill
    c.setFillColor(HexColor('#009cb6'))
    c.rect(bar_left, bar_y, bar_width_inner * (fuel_percent / 100), 15, fill=1, stroke=0)
    
    # Fuel level text
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(HexColor('#009cb6'))
    c.drawCentredString(40 + box_width / 2, y_pos - 165, fuel_level)
    
    # Right box - Return date (YELLOW/AMBER like in history)
    if inspection_data['inspection_type'] == 'checkin':
        box_color = HexColor('#fef3c7')  # bg-amber-50
        border_color = HexColor('#f59e0b')  # border-amber-500
        title_color = HexColor('#b45309')  # text-amber-700
        
        c.setFillColor(box_color)
        c.rect(50 + box_width, y_pos - box_height, box_width, box_height, fill=1, stroke=0)
        
        c.setStrokeColor(border_color)
        c.setLineWidth(1)
        c.rect(50 + box_width, y_pos - box_height, box_width, box_height, fill=0, stroke=1)
        
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(title_color)
        c.drawString(60 + box_width, y_pos - 25, "Recolha (Check-Out) - Prevista")
        
        c.setFont("Helvetica", 9)
        c.setFillColor(HexColor('#4b5563'))
        c.drawString(60 + box_width, y_pos - 45, "Data:")
        c.setFont("Helvetica-Bold", 9)
        return_date = extracted.get('returnDate') or extracted.get('return_date', 'N/A')
        c.drawString(130 + box_width, y_pos - 45, return_date)
        
        c.setFont("Helvetica", 9)
        c.setFillColor(HexColor('#4b5563'))
        c.drawString(60 + box_width, y_pos - 60, "Estado:")
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(HexColor('#f59e0b'))
        c.drawString(130 + box_width, y_pos - 60, "Pendente")
    
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
                if y_start < 150:
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
        
        y_pos = y_start - photo_size - 30
    
    # "Entregue por" section after photos
    if y_pos < 150:
        c.showPage()
        y_pos = height - 60
    
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(HexColor('#1f2937'))
    
    # Get first and last name
    inspector_name = inspection_data.get('inspector_name', 'N/A')
    if inspector_name and inspector_name != 'N/A':
        name_parts = inspector_name.split()
        if len(name_parts) >= 2:
            short_name = f"{name_parts[0]} {name_parts[-1]}"
        else:
            short_name = inspector_name
    else:
        short_name = 'N/A'
    
    date_time_str = inspection_data['created_at'].strftime('%d/%m/%Y às %H:%M') if inspection_data.get('created_at') else 'N/A'
    
    c.drawString(40, y_pos, f"Entregue por: {short_name}")
    c.setFont("Helvetica", 10)
    c.setFillColor(HexColor('#4b5563'))
    c.drawString(40, y_pos - 15, date_time_str)
    
    y_pos -= 40
    
    # Footer with company info (like in image)
    footer_height = 80
    footer_y = footer_height
    
    # Cyan footer bar
    c.setFillColor(HexColor('#009cb6'))
    c.rect(0, 0, width, 35, fill=1, stroke=0)
    
    # Copyright text in cyan bar
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(HexColor('#ffffff'))
    c.drawCentredString(width / 2, 12, "© 2026 Auto Prudente Rent a Car. Todos os direitos reservados.")
    
    # Company details above cyan bar
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(HexColor('#4b5563'))
    c.drawCentredString(width / 2, 70, "Auto Prudente Rent a Car Unipessoal, Lda. - Número Fiscal: PT 503 539 791")
    
    c.setFont("Helvetica", 8)
    c.setFillColor(HexColor('#6b7280'))
    c.drawCentredString(width / 2, 58, "Sede: Estrada de Santa Eulália, Edifício Onda do Mar Loja E, 8200-269 Albufeira")
    
    c.setFont("Helvetica", 8)
    phone_email = "Telefone +351 289 542 160 | E-mail: info@auto-prudente.com"
    c.drawCentredString(width / 2, 46, phone_email)
    
    c.save()
    buffer.seek(0)
    return buffer.getvalue()
