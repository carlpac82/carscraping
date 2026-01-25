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
    
    # DEBUG: Console prints
    print("\n" + "="*80)
    print("🔍 DEBUG PDF GENERATION")
    print("="*80)
    print(f"📋 inspection_data keys: {list(inspection_data.keys())}")
    print(f"⛽ fuel_level: '{inspection_data.get('fuel_level')}' (type: {type(inspection_data.get('fuel_level'))})")
    print(f"👤 client_name: '{inspection_data.get('client_name')}'")
    print(f"📦 extracted keys: {list(extracted.keys()) if extracted else 'None'}")
    if extracted:
        print(f"   - client_name (snake): '{extracted.get('client_name')}'")
        print(f"   - clientName (camel): '{extracted.get('clientName')}'")
        print(f"   - customerName: '{extracted.get('customerName')}'")
        print(f"   - name: '{extracted.get('name')}'")
    print("="*80 + "\n")
    
    # Create PDF
    buffer = io.BytesIO()
    c = pdf_canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Cyan header bar (smaller)
    header_height = 50
    header_color = HexColor('#009cb6')
    c.setFillColor(header_color)
    c.rect(0, height - header_height, width, header_height, fill=1, stroke=0)
    
    # Logo on left (smaller)
    logo_path = 'static/ap-heather.png'
    if os.path.exists(logo_path):
        try:
            c.drawImage(logo_path, 20, height - 45, width=100, height=35, preserveAspectRatio=True, mask='auto')
        except Exception as e:
            logging.warning(f"Could not load logo: {e}")
    else:
        # Try alternative path
        logo_path = '/app/static/ap-heather.png'
        if os.path.exists(logo_path):
            try:
                c.drawImage(logo_path, 20, height - 45, width=100, height=35, preserveAspectRatio=True, mask='auto')
            except Exception as e:
                logging.warning(f"Could not load logo: {e}")
    
    # Title in center of header (uppercase, vertically centered)
    c.setFillColor(HexColor('#ffffff'))
    c.setFont("Helvetica-Bold", 14)
    
    if inspection_data['inspection_type'] == 'checkin':
        title = "RELATÓRIO DE ENTREGA"
    elif inspection_data['inspection_type'] == 'self_checkout':
        title = "RELATÓRIO DE DEVOLUÇÃO"
    else:
        title = "RELATÓRIO DE DEVOLUÇÃO"
    
    # Center vertically in header (header_height = 50)
    c.drawCentredString(width / 2, height - 30, title)
    
    # RA number on right in header (much smaller)
    c.setFillColor(HexColor('#ffffff'))
    c.setFont("Helvetica-Bold", 11)
    ra_text = f"R.A.: {inspection_data['contract_number']}"
    ra_width = c.stringWidth(ra_text, "Helvetica-Bold", 11)
    
    # Box for RA (much smaller)
    box_padding = 8
    box_x = width - ra_width - box_padding * 2 - 20
    box_y = height - 35
    c.setFillColor(HexColor('#ffffff'))
    c.setFillColorRGB(1, 1, 1, alpha=0.2)
    c.roundRect(box_x, box_y, ra_width + box_padding * 2, 18, 3, fill=1, stroke=0)
    
    c.setFillColor(HexColor('#ffffff'))
    c.drawString(box_x + box_padding, box_y + 5, ra_text)
    
    # Start content below header
    y_pos = height - 60
    
    # Gray box with vehicle info (smaller) - same width as other boxes
    box_height = 60
    total_width = width - 80  # Same width for all boxes
    c.setFillColor(HexColor('#f9fafb'))  # bg-gray-50
    c.roundRect(40, y_pos - box_height, total_width, box_height, 5, fill=1, stroke=0)
    
    # Grid 3 columns inside gray box (smaller fonts)
    col_width = (total_width - 20) / 3
    
    # Row 1
    row_y = y_pos - 15
    
    # Marca
    c.setFont("Helvetica", 8)
    c.setFillColor(HexColor('#6b7280'))
    c.drawString(50, row_y, "Marca")
    c.setFont("Helvetica-Bold", 9)
    # Extract brand - prioritize inspection_data, then extracted_data_json
    brand = inspection_data.get('vehicle_brand') or ''
    if not brand:
        brand = extracted.get('vehicleBrand') or extracted.get('brand') or extracted.get('make') or 'N/A'
    c.drawString(50, row_y - 10, brand)
    
    # Modelo
    c.setFont("Helvetica", 8)
    c.setFillColor(HexColor('#6b7280'))
    c.drawString(50 + col_width, row_y, "Modelo")
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(HexColor('#111827'))
    # Extract model - prioritize inspection_data, then extracted_data_json
    model = inspection_data.get('vehicle_model') or ''
    if not model:
        model = extracted.get('vehicleModel') or extracted.get('model') or 'N/A'
    c.drawString(50 + col_width, row_y - 10, model)
    
    # Matrícula
    c.setFont("Helvetica", 8)
    c.setFillColor(HexColor('#6b7280'))
    c.drawString(50 + col_width * 2, row_y, "Matrícula")
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(HexColor('#111827'))
    c.drawString(50 + col_width * 2, row_y - 10, inspection_data.get('vehicle_plate', 'N/A'))
    
    # Row 2
    row_y -= 28
    
    # Contrato (RA)
    c.setFont("Helvetica", 8)
    c.setFillColor(HexColor('#6b7280'))
    c.drawString(50, row_y, "Contrato (RA)")
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(HexColor('#111827'))
    c.drawString(50, row_y - 10, inspection_data['contract_number'])
    
    # Cliente
    c.setFont("Helvetica", 8)
    c.setFillColor(HexColor('#6b7280'))
    c.drawString(50 + col_width, row_y, "Cliente")
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(HexColor('#111827'))
    # Extract client name - prioritize inspection_data, then extracted_data_json
    client_name = inspection_data.get('client_name') or ''
    if not client_name:
        client_name = (
            extracted.get('clientName') or 
            extracted.get('client_name') or 
            extracted.get('customerName') or 
            'N/A'
        )
    print(f"✅ Final client_name used: '{client_name}'")
    c.drawString(50 + col_width, row_y - 10, client_name)
    
    y_pos -= box_height + 15
    
    # Helper function to convert fuel level to percentage
    def fuel_to_percent(fuel_level):
        fuel_map = {'R': 0, '1/8': 12.5, '1/4': 25, '3/8': 37.5, '1/2': 50, '5/8': 62.5, '3/4': 75, '7/8': 87.5, 'F': 100}
        return fuel_map.get(fuel_level, 0)
    
    # Two boxes side by side (no title)
    box_width = (width - 100) / 2
    box_height = 120
    
    # Left box - Check-in/Check-out info (colors match website)
    if inspection_data['inspection_type'] == 'checkin':
        box_color = HexColor('#e6f7fa')  # bg heather light blue
        border_color = HexColor('#009cb6')  # border heather cyan
        title_color = HexColor('#009cb6')  # heather cyan
    else:
        box_color = HexColor('#fffbeb')  # bg-yellow-50
        border_color = HexColor('#fbbf24')  # border-yellow-400
        title_color = HexColor('#d97706')  # text-yellow-600
    
    c.setFillColor(box_color)
    c.roundRect(40, y_pos - box_height, box_width, box_height, 8, fill=1, stroke=0)
    
    c.setStrokeColor(border_color)
    c.setLineWidth(1)
    c.roundRect(40, y_pos - box_height, box_width, box_height, 8, fill=0, stroke=1)
    
    # Title with icon space
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(title_color)
    if inspection_data['inspection_type'] == 'checkin':
        c.drawString(50, y_pos - 18, "Entrega (Check-In)")
    else:
        c.drawString(50, y_pos - 18, "Recolha (Check-Out)")
    
    # Content with flex layout (label left, value right)
    content_y = y_pos - 38
    label_x = 50
    value_x = 40 + box_width - 10
    
    # For checkout, show Local de Recolha first, then Data de Recolha Esperada
    if inspection_data['inspection_type'] == 'checkout':
        # Local de Recolha
        c.setFont("Helvetica", 8)
        c.setFillColor(HexColor('#6b7280'))
        c.drawString(label_x, content_y, "Local de Recolha:")
        location = (inspection_data.get('return_location') or 
                    extracted.get('returnLocation') or 
                    extracted.get('return_location') or 
                    'N/A')
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(HexColor('#111827'))
        c.drawRightString(value_x, content_y, location)
        
        content_y -= 12
        c.setFont("Helvetica", 8)
        c.setFillColor(HexColor('#6b7280'))
        c.drawString(label_x, content_y, "Data:")
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(HexColor('#111827'))
        # Format date as dd/mm/yyyy HH:MM
        if inspection_data.get('created_at'):
            date_str = inspection_data['created_at'].strftime('%d/%m/%Y %H:%M')
        else:
            return_date = inspection_data.get('return_date') or 'N/A'
            return_time = inspection_data.get('return_time') or ''
            date_str = f"{return_date} {return_time}".strip() if return_date != 'N/A' else 'N/A'
        c.drawRightString(value_x, content_y, date_str)
    else:
        # For checkin, show Local de Entrega and Data
        c.setFont("Helvetica", 8)
        c.setFillColor(HexColor('#6b7280'))
        c.drawString(label_x, content_y, "Local de Entrega:")
        location = (inspection_data.get('pickup_location') or 
                    extracted.get('pickupLocation') or 
                    extracted.get('pickup_location') or 
                    'N/A')
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(HexColor('#111827'))
        c.drawRightString(value_x, content_y, location)
        
        content_y -= 12
        c.setFont("Helvetica", 8)
        c.setFillColor(HexColor('#6b7280'))
        c.drawString(label_x, content_y, "Data:")
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(HexColor('#111827'))
        date_str = inspection_data['created_at'].strftime('%d/%m/%Y %H:%M') if inspection_data.get('created_at') else 'N/A'
        c.drawRightString(value_x, content_y, date_str)
    
    content_y -= 12
    c.setFont("Helvetica", 8)
    c.setFillColor(HexColor('#6b7280'))
    if inspection_data['inspection_type'] == 'checkin':
        c.drawString(label_x, content_y, "Entregue por:")
    else:
        c.drawString(label_x, content_y, "Recolhido por:")
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(HexColor('#111827'))
    inspector = inspection_data.get('inspector_name', 'N/A')
    if inspector and inspector != 'N/A':
        parts = inspector.split()
        if len(parts) >= 2:
            inspector = f"{parts[0]} {parts[-1]}"
    c.drawRightString(value_x, content_y, inspector)
    
    content_y -= 12
    c.setFont("Helvetica", 8)
    c.setFillColor(HexColor('#6b7280'))
    c.drawString(label_x, content_y, "Quilómetros:")
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(HexColor('#111827'))
    odometer = inspection_data.get('odometer_reading', 'N/A')
    if odometer and odometer != 'N/A':
        try:
            odometer_str = f"{int(odometer):,} km".replace(',', ' ')
        except (ValueError, TypeError):
            odometer_str = f"{odometer} km"
    else:
        odometer_str = 'N/A'
    c.drawRightString(value_x, content_y, odometer_str)
    
    content_y -= 12
    c.setFont("Helvetica", 8)
    c.setFillColor(HexColor('#6b7280'))
    c.drawString(label_x, content_y, "Danos:")
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(HexColor('#111827'))
    c.drawRightString(value_x, content_y, "4")
    
    # Process fuel level for later use
    fuel_level = inspection_data.get('fuel_level') or 'R'
    print(f"⛽ Raw fuel_level: '{fuel_level}' (type: {type(fuel_level)})")
    
    # Convert string to number if needed
    if isinstance(fuel_level, str) and fuel_level.strip().replace('.', '', 1).isdigit():
        try:
            fuel_level = float(fuel_level) if '.' in fuel_level else int(fuel_level)
        except (ValueError, TypeError):
            pass
    
    # Convert numeric fuel level to fraction if needed
    if isinstance(fuel_level, (int, float)):
        if fuel_level == 0:
            fuel_level = 'R'
        elif fuel_level <= 12.5:
            fuel_level = '1/8'
        elif fuel_level <= 25:
            fuel_level = '1/4'
        elif fuel_level <= 37.5:
            fuel_level = '3/8'
        elif fuel_level <= 50:
            fuel_level = '1/2'
        elif fuel_level <= 62.5:
            fuel_level = '5/8'
        elif fuel_level <= 75:
            fuel_level = '3/4'
        elif fuel_level <= 87.5:
            fuel_level = '7/8'
        else:
            fuel_level = 'F'
    print(f"✅ Converted fuel_level: '{fuel_level}'")
    fuel_percent = fuel_to_percent(fuel_level)
    print(f"📊 Fuel percent: {fuel_percent}%")
    
    # Right box - Return date (YELLOW/AMBER)
    if inspection_data['inspection_type'] == 'checkin':
        box_color = HexColor('#fffbeb')  # bg-amber-50 (lighter)
        border_color = HexColor('#fde68a')  # border-amber-200
        title_color = HexColor('#d97706')  # text-amber-600
        
        c.setFillColor(box_color)
        c.roundRect(50 + box_width, y_pos - box_height, box_width, box_height, 8, fill=1, stroke=0)
        
        c.setStrokeColor(border_color)
        c.setLineWidth(1)
        c.roundRect(50 + box_width, y_pos - box_height, box_width, box_height, 8, fill=0, stroke=1)
        
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(title_color)
        c.drawString(60 + box_width, y_pos - 18, "Recolha (Check-Out)")
        
        content_y = y_pos - 38
        label_x = 60 + box_width
        value_x = 50 + box_width * 2 - 10
        
        # Local de Recolha
        c.setFont("Helvetica", 8)
        c.setFillColor(HexColor('#6b7280'))
        c.drawString(label_x, content_y, "Local de Recolha:")
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(HexColor('#111827'))
        return_location = (extracted.get('returnLocation') or 
                          extracted.get('return_location') or 
                          inspection_data.get('return_location') or 
                          'N/A')
        c.drawRightString(value_x, content_y, return_location)
        
        content_y -= 12
        
        # Data
        c.setFont("Helvetica", 8)
        c.setFillColor(HexColor('#6b7280'))
        c.drawString(label_x, content_y, "Data:")
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(HexColor('#111827'))
        # Try to get date and time
        return_date = extracted.get('returnDate') or extracted.get('return_date', 'N/A')
        return_time = extracted.get('returnTime') or extracted.get('return_time', '')
        
        # Normalize date format from "21 - 01 - 2026" to "21/01/2026"
        if return_date and return_date != 'N/A':
            return_date = return_date.replace(' - ', '/').replace('-', '/')
        
        # Normalize time format from "10 : 00" to "10:00"
        if return_time:
            return_time = return_time.replace(' : ', ':').replace(' :', ':').replace(': ', ':')
            return_datetime = f"{return_date} {return_time}".strip()
        else:
            return_datetime = return_date
        c.drawRightString(value_x, content_y, return_datetime)
        
        content_y -= 12
        c.setFont("Helvetica", 8)
        c.setFillColor(HexColor('#6b7280'))
        c.drawString(label_x, content_y, "Estado:")
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(HexColor('#f59e0b'))
        c.drawRightString(value_x, content_y, "Pendente")
    
    y_pos -= box_height + 15
    
    # Croqui de Danos e Informações da Entrega (side by side)
    if inspection_data.get('damage_croqui'):
        try:
            croqui_data = inspection_data['damage_croqui']
            if croqui_data.startswith('data:image'):
                croqui_data = croqui_data.split(',')[1]
            
            img_data = base64.b64decode(croqui_data)
            img = Image.open(io.BytesIO(img_data))
            
            # Convert to RGB if needed
            if img.mode == 'RGBA':
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Two boxes side by side - same dimensions as check-in/checkout boxes
            total_width = width - 80
            box_spacing = 10
            left_box_width = (total_width - box_spacing) / 2
            right_box_width = (total_width - box_spacing) / 2
            box_height_croqui = 120  # Same height as check-in/checkout boxes
            
            # Left box - Info box with border (like check-in card)
            box_color = HexColor('#e6f7fa')  # bg heather light blue
            border_color = HexColor('#009cb6')  # border heather cyan
            
            c.setFillColor(box_color)
            c.roundRect(40, y_pos - box_height_croqui, left_box_width, box_height_croqui, 8, fill=1, stroke=0)
            
            c.setStrokeColor(border_color)
            c.setLineWidth(1)
            c.roundRect(40, y_pos - box_height_croqui, left_box_width, box_height_croqui, 8, fill=0, stroke=1)
            
            # Content in left box - centered layout
            box_center_x = 40 + left_box_width / 2
            content_y = y_pos - 30
            
            # Quilómetros label centered
            c.setFont("Helvetica", 8)
            c.setFillColor(HexColor('#6b7280'))
            c.drawCentredString(box_center_x, content_y, "Quilómetros:")
            
            content_y -= 12
            
            # Quilómetros value centered
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(HexColor('#111827'))
            c.drawCentredString(box_center_x, content_y, odometer_str)
            
            content_y -= 20
            
            # Combustível label centered
            c.setFont("Helvetica", 8)
            c.setFillColor(HexColor('#6b7280'))
            c.drawCentredString(box_center_x, content_y, "Combustível:")
            
            content_y -= 12
            
            # Fuel bar centered in box
            bar_width_inner = (left_box_width - 40) * 0.7
            bar_left = 40 + (left_box_width - bar_width_inner) / 2
            bar_height = 16
            
            # Fuel markers
            c.setFont("Helvetica-Bold", 7)
            c.setFillColor(HexColor('#009cb6'))
            c.drawString(bar_left - 8, content_y, "R")
            c.drawCentredString(bar_left + bar_width_inner * 0.25, content_y, "1/4")
            c.drawCentredString(bar_left + bar_width_inner * 0.5, content_y, "1/2")
            c.drawCentredString(bar_left + bar_width_inner * 0.75, content_y, "3/4")
            c.drawString(bar_left + bar_width_inner + 5, content_y, "F")
            
            content_y -= 12
            
            # Background bar (white with cyan border)
            c.setStrokeColor(HexColor('#009cb6'))
            c.setLineWidth(2)
            c.setFillColor(HexColor('#ffffff'))
            c.roundRect(bar_left, content_y, bar_width_inner, bar_height, 5, fill=1, stroke=1)
            
            # Fuel bar fill (cyan, rounded, INSIDE the border)
            if fuel_percent > 0:
                c.setFillColor(HexColor('#009cb6'))
                fill_width = max(10, (bar_width_inner - 4) * (fuel_percent / 100))
                c.roundRect(bar_left + 2, content_y + 2, fill_width, bar_height - 4, 4, fill=1, stroke=0)
            
            # Fuel bar markers (vertical lines)
            c.setStrokeColor(HexColor('#009cb6'))
            c.setLineWidth(0.5)
            for pos in [0, 0.25, 0.5, 0.75, 1.0]:
                x = bar_left + bar_width_inner * pos
                c.line(x, content_y + 3, x, content_y + bar_height - 3)
            
            # Right box - Croqui with border
            right_box_x = 40 + left_box_width + box_spacing
            c.setFillColor(HexColor('#ffffff'))
            c.setStrokeColor(HexColor('#d1d5db'))
            c.setLineWidth(1)
            c.roundRect(right_box_x, y_pos - box_height_croqui, right_box_width, box_height_croqui, 8, fill=1, stroke=1)
            
            # Calculate croqui size to fit right box
            img_width = right_box_width - 20  # padding inside border
            img_height = img_width * img.height / img.width
            
            # Limit height
            if img_height > box_height_croqui - 20:
                img_height = box_height_croqui - 20
                img_width = img_height * img.width / img.height
            
            # Center croqui in right box
            x_pos = right_box_x + (right_box_width - img_width) / 2
            y_img_pos = y_pos - box_height_croqui + (box_height_croqui - img_height) / 2
            
            # Draw croqui
            c.drawImage(ImageReader(img), x_pos, y_img_pos, width=img_width, height=img_height)
            
            y_pos -= box_height_croqui + 15
        except Exception as e:
            logging.error(f"Error adding croqui to PDF: {e}")
    
    # Photos grid (3x3 - fill rectangles)
    photos = inspection_data.get('photos', [])
    if photos:
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(HexColor('#1f2937'))
        c.drawString(40, y_pos, "Fotografias da Inspeção")
        y_pos -= 15
        
        # Grid settings - same width as croqui box
        cols = 3
        grid_total_width = width - 80  # Same as croqui border_width
        spacing_horizontal = 10
        photo_width = (grid_total_width - spacing_horizontal * 2) / cols
        photo_height = photo_width * 0.6  # Smaller ratio
        spacing_vertical = 15  # Increased vertical spacing
        
        # Photo labels
        photo_labels = [
            "Frente", "Frente Esquerda", "Lado Esquerdo",
            "Traseira Esquerda", "Traseira", "Traseira Direita",
            "Lado Direito", "Frente Direita", "Conta-Quilómetros"
        ]
        
        x_start = 40
        y_start = y_pos
        
        for idx, photo in enumerate(photos[:9]):
            if idx > 0 and idx % cols == 0:
                y_start -= photo_height + spacing_vertical + 8
            
            col = idx % cols
            x = x_start + col * (photo_width + spacing_horizontal)
            y = y_start - photo_height
            
            try:
                photo_data = photo['image_data']
                if photo_data.startswith('data:image'):
                    photo_data = photo_data.split(',')[1]
                
                img_data = base64.b64decode(photo_data)
                img = Image.open(io.BytesIO(img_data))
                
                # Draw white background with rounded corners
                c.setFillColor(HexColor('#ffffff'))
                c.roundRect(x, y, photo_width, photo_height, 6, fill=1, stroke=0)
                
                # Save state for clipping
                c.saveState()
                
                # Create rounded rectangle clipping path
                p = c.beginPath()
                radius = 6
                p.moveTo(x + radius, y)
                p.lineTo(x + photo_width - radius, y)
                p.arcTo(x + photo_width - radius, y, x + photo_width, y + radius, radius)
                p.lineTo(x + photo_width, y + photo_height - radius)
                p.arcTo(x + photo_width, y + photo_height - radius, x + photo_width - radius, y + photo_height, radius)
                p.lineTo(x + radius, y + photo_height)
                p.arcTo(x + radius, y + photo_height, x, y + photo_height - radius, radius)
                p.lineTo(x, y + radius)
                p.arcTo(x, y + radius, x + radius, y, radius)
                p.close()
                c.clipPath(p, stroke=0, fill=0)
                
                # Calculate cover fit dimensions
                img_width, img_height = img.size
                img_aspect = img_width / img_height
                photo_aspect = photo_width / photo_height
                
                if img_aspect > photo_aspect:
                    # Image is wider - fit to height and crop width (cover fit)
                    draw_height = photo_height
                    draw_width = draw_height * img_aspect
                    draw_x = x - (draw_width - photo_width) / 2
                    draw_y = y
                else:
                    # Image is taller - fit to width and crop height (cover fit)
                    draw_width = photo_width
                    draw_height = draw_width / img_aspect
                    draw_x = x
                    draw_y = y - (draw_height - photo_height) / 2
                
                # Draw image with cover fit
                c.drawImage(ImageReader(img), draw_x, draw_y, width=draw_width, height=draw_height, mask='auto')
                
                # Restore state to remove clipping
                c.restoreState()
                
                # Draw rounded border
                c.setStrokeColor(HexColor('#d1d5db'))
                c.setLineWidth(0.5)
                c.roundRect(x, y, photo_width, photo_height, 6, fill=0, stroke=1)
                
                # Draw label below photo
                c.setFont("Helvetica", 5)
                c.setFillColor(HexColor('#6b7280'))
                label = photo_labels[idx] if idx < len(photo_labels) else f"Foto {idx + 1}"
                c.drawCentredString(x + photo_width / 2, y - 6, label)
            except Exception as e:
                logging.error(f"Error adding photo {idx} to PDF: {e}")
        
        y_pos = y_start - (photo_height + spacing_vertical + 8) * 3 - 15
    
    # Footer with company info (no "Entregue por" section - it's already in the card)
    # Cyan footer bar
    c.setFillColor(HexColor('#009cb6'))
    c.rect(0, 0, width, 50, fill=1, stroke=0)
    
    # Company details in cyan footer (smaller text)
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(HexColor('#ffffff'))
    c.drawCentredString(width / 2, 35, "Auto Prudente Rent a Car Unipessoal, Lda. - Número Fiscal: PT 503 539 791")
    
    c.setFont("Helvetica", 6)
    c.setFillColor(HexColor('#ffffff'))
    c.drawCentredString(width / 2, 25, "Sede: Estrada de Santa Eulália, Edifício Onda do Mar Loja E, 8200-269 Albufeira")
    
    c.setFont("Helvetica", 6)
    phone_email = "Telefone +351 289 542 160 | E-mail: info@auto-prudente.com"
    c.drawCentredString(width / 2, 15, phone_email)
    
    c.save()
    buffer.seek(0)
    return buffer.getvalue()
