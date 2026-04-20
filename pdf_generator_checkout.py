"""Modern PDF generator for vehicle inspections - v2026.04.20.10:02"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas as pdf_canvas
import io
import os
import json
import logging
import base64
from PIL import Image, ImageDraw
from reportlab.lib.utils import ImageReader

def generate_inspection_pdf(inspection_data, extracted_data_json):
    """Generate a modern, clean PDF for check-in, check-out, or self-checkout inspection"""
    
    # CRITICAL: Version check - if you don't see this, Railway is using cached version
    print("=" * 80, flush=True)
    print("🚨🚨🚨 PDF GENERATOR v2026.04.20.10:05 LOADED 🚨🚨🚨", flush=True)
    print("=" * 80, flush=True)
    logging.info("🚨🚨🚨 PDF GENERATOR v2026.04.20.10:05 LOADED 🚨🚨🚨")
    
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
    
    # Two boxes side by side - same width calculation as croqui boxes
    total_width = width - 80
    box_spacing = 10
    box_width = (total_width - box_spacing) / 2
    box_height = 120
    
    is_checkout = inspection_data['inspection_type'] == 'checkout'
    
    # Left box - SEMPRE Entrega (Check-In) - azul
    box_color_left = HexColor('#e6f7fa')  # bg heather light blue
    border_color_left = HexColor('#009cb6')  # border heather cyan
    title_color_left = HexColor('#009cb6')  # heather cyan
    
    c.setFillColor(box_color_left)
    c.roundRect(40, y_pos - box_height, box_width, box_height, 8, fill=1, stroke=0)
    
    c.setStrokeColor(border_color_left)
    c.setLineWidth(1)
    c.roundRect(40, y_pos - box_height, box_width, box_height, 8, fill=0, stroke=1)
    
    # Title caixa azul
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(title_color_left)
    c.drawString(50, y_pos - 18, "Entrega (Check-In)")
    
    # Content caixa azul
    content_y_left = y_pos - 38
    label_x_left = 50
    value_x_left = 40 + box_width - 10
    
    # Local de Entrega
    c.setFont("Helvetica", 8)
    c.setFillColor(HexColor('#6b7280'))
    c.drawString(label_x_left, content_y_left, "Local de Entrega:")
    location_checkin = (inspection_data.get('pickup_location') or 
                extracted.get('pickupLocation') or 
                extracted.get('pickup_location') or 
                'N/A')
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(HexColor('#111827'))
    c.drawRightString(value_x_left, content_y_left, location_checkin)
    
    content_y_left -= 12
    
    # Data
    c.setFont("Helvetica", 8)
    c.setFillColor(HexColor('#6b7280'))
    c.drawString(label_x_left, content_y_left, "Data:")
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(HexColor('#111827'))
    if is_checkout and inspection_data.get('checkin_created_at'):
        date_str_checkin = inspection_data['checkin_created_at'].strftime('%d/%m/%Y %H:%M')
    else:
        date_str_checkin = inspection_data['created_at'].strftime('%d/%m/%Y %H:%M') if inspection_data.get('created_at') else 'N/A'
    c.drawRightString(value_x_left, content_y_left, date_str_checkin)
    
    content_y_left -= 12
    
    # Entregue por
    c.setFont("Helvetica", 8)
    c.setFillColor(HexColor('#6b7280'))
    c.drawString(label_x_left, content_y_left, "Entregue por:")
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(HexColor('#111827'))
    inspector_checkin = inspection_data.get('inspector_name', 'N/A')
    if inspector_checkin and inspector_checkin != 'N/A':
        parts = inspector_checkin.split()
        if len(parts) >= 2:
            inspector_checkin = f"{parts[0]} {parts[-1]}"
    c.drawRightString(value_x_left, content_y_left, inspector_checkin)
    
    # Right box - Recolha (Check-Out) se for checkout, ou Recolha Prevista se for checkin
    right_box_x = 40 + box_width + box_spacing
    
    if is_checkout:
        # Caixa amarela - Recolha (Check-Out)
        box_color_right = HexColor('#fffbeb')  # bg-yellow-50
        border_color_right = HexColor('#fbbf24')  # border-yellow-400
        title_color_right = HexColor('#d97706')  # text-yellow-600
        
        c.setFillColor(box_color_right)
        c.roundRect(right_box_x, y_pos - box_height, box_width, box_height, 8, fill=1, stroke=0)
        
        c.setStrokeColor(border_color_right)
        c.setLineWidth(1)
        c.roundRect(right_box_x, y_pos - box_height, box_width, box_height, 8, fill=0, stroke=1)
        
        # Title caixa amarela
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(title_color_right)
        c.drawString(right_box_x + 10, y_pos - 18, "Recolha (Check-Out)")
        
        # Content caixa amarela
        content_y_right = y_pos - 38
        label_x_right = right_box_x + 10
        value_x_right = right_box_x + box_width - 10
        
        # Local de Recolha
        c.setFont("Helvetica", 8)
        c.setFillColor(HexColor('#6b7280'))
        c.drawString(label_x_right, content_y_right, "Local de Recolha:")
        location_checkout = (inspection_data.get('return_location') or 
                    extracted.get('returnLocation') or 
                    extracted.get('return_location') or 
                    'N/A')
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(HexColor('#111827'))
        c.drawRightString(value_x_right, content_y_right, location_checkout)
        
        content_y_right -= 12
        
        # Data
        c.setFont("Helvetica", 8)
        c.setFillColor(HexColor('#6b7280'))
        c.drawString(label_x_right, content_y_right, "Data:")
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(HexColor('#111827'))
        date_str_checkout = inspection_data['created_at'].strftime('%d/%m/%Y %H:%M') if inspection_data.get('created_at') else 'N/A'
        c.drawRightString(value_x_right, content_y_right, date_str_checkout)
        
        content_y_right -= 12
        
        # Recolhido por
        c.setFont("Helvetica", 8)
        c.setFillColor(HexColor('#6b7280'))
        c.drawString(label_x_right, content_y_right, "Recolhido por:")
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(HexColor('#111827'))
        inspector_checkout = inspection_data.get('inspector_name', 'N/A')
        if inspector_checkout and inspector_checkout != 'N/A':
            parts = inspector_checkout.split()
            if len(parts) >= 2:
                inspector_checkout = f"{parts[0]} {parts[-1]}"
        c.drawRightString(value_x_right, content_y_right, inspector_checkout)
    else:
        # Caixa amarela - Recolha Prevista (check-in)
        box_color_right = HexColor('#fffbeb')  # bg-yellow-50
        border_color_right = HexColor('#fbbf24')  # border-yellow-400
        title_color_right = HexColor('#d97706')  # text-yellow-600
        
        c.setFillColor(box_color_right)
        c.roundRect(right_box_x, y_pos - box_height, box_width, box_height, 8, fill=1, stroke=0)
        
        c.setStrokeColor(border_color_right)
        c.setLineWidth(1)
        c.roundRect(right_box_x, y_pos - box_height, box_width, box_height, 8, fill=0, stroke=1)
        
        # Title
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(title_color_right)
        c.drawString(right_box_x + 10, y_pos - 18, "Recolha (Check-Out)")
        
        # Content
        content_y_right = y_pos - 38
        label_x_right = right_box_x + 10
        value_x_right = right_box_x + box_width - 10
        
        # Local de Recolha
        c.setFont("Helvetica", 8)
        c.setFillColor(HexColor('#6b7280'))
        c.drawString(label_x_right, content_y_right, "Local de Recolha:")
        location = (inspection_data.get('return_location') or 
                    extracted.get('returnLocation') or 
                    extracted.get('return_location') or 
                    'N/A')
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(HexColor('#111827'))
        c.drawRightString(value_x_right, content_y_right, location)
        
        content_y_right -= 12
        
        # Data
        c.setFont("Helvetica", 8)
        c.setFillColor(HexColor('#6b7280'))
        c.drawString(label_x_right, content_y_right, "Data:")
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(HexColor('#111827'))
        return_date = extracted.get('returnDate') or extracted.get('return_date') or 'N/A'
        return_time = extracted.get('returnTime') or extracted.get('return_time') or ''
        if return_date and return_date != 'N/A':
            return_date = return_date.replace(' - ', '/').replace('-', '/')
            if return_time:
                return_time = return_time.replace(' : ', ':').replace(' :', ':').replace(': ', ':')
                return_datetime = f"{return_date} {return_time}".strip()
            else:
                return_datetime = return_date
        else:
            return_datetime = 'N/A'
        c.drawRightString(value_x_right, content_y_right, return_datetime)
        
        content_y_right -= 12
        
        # Estado
        c.setFont("Helvetica", 8)
        c.setFillColor(HexColor('#6b7280'))
        c.drawString(label_x_right, content_y_right, "Estado:")
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(HexColor('#f59e0b'))
        c.drawRightString(value_x_right, content_y_right, "Pendente")
    
    # Process odometer and fuel for check-in (blue box)
    is_checkout = inspection_data.get('inspection_type') == 'checkout'
    
    print(f"🔍 DEBUG - inspection_data keys: {inspection_data.keys()}")
    print(f"🔍 DEBUG - checkin_odometer: '{inspection_data.get('checkin_odometer')}'")
    print(f"🔍 DEBUG - checkin_fuel: '{inspection_data.get('checkin_fuel')}'")
    print(f"🔍 DEBUG - checkin_created_at: '{inspection_data.get('checkin_created_at')}'")
    print(f"🔍 DEBUG - odometer_reading: '{inspection_data.get('odometer_reading')}'")
    print(f"🔍 DEBUG - fuel_level: '{inspection_data.get('fuel_level')}'")
    
    if is_checkout:
        # Para checkout, usar dados do check-in na caixa azul
        checkin_odometer = inspection_data.get('checkin_odometer', 'N/A')
        checkin_odometer_raw = 0
        if checkin_odometer and checkin_odometer != 'N/A' and checkin_odometer != '':
            try:
                checkin_odometer_raw = int(checkin_odometer)
                odometer_str = f"{checkin_odometer_raw:,} km".replace(',', ' ')
            except (ValueError, TypeError):
                odometer_str = f"{checkin_odometer} km"
        else:
            odometer_str = 'N/A'
        
        print(f"🔵 Check-in odometer: {checkin_odometer} -> {odometer_str}")
        
        # Fuel do check-in para a caixa azul
        fuel_level = inspection_data.get('checkin_fuel') or 'R'
        print(f"🔵 Check-in fuel: {fuel_level}")
        
        # Processar também dados do checkout para a caixa amarela
        checkout_odometer = inspection_data.get('odometer_reading', 'N/A')
        checkout_odometer_raw = 0
        if checkout_odometer and checkout_odometer != 'N/A':
            try:
                checkout_odometer_raw = int(checkout_odometer)
                checkout_odometer_str = f"{checkout_odometer_raw:,} km".replace(',', ' ')
            except (ValueError, TypeError):
                checkout_odometer_str = f"{checkout_odometer} km"
        else:
            checkout_odometer_str = 'N/A'
        
        print(f"🟡 Check-out odometer: {checkout_odometer} -> {checkout_odometer_str}")
        
        # Calcular quilómetros percorridos
        percorridos_str = 'N/A'
        if checkin_odometer_raw > 0 and checkout_odometer_raw > 0:
            percorridos = checkout_odometer_raw - checkin_odometer_raw
            if percorridos >= 0:
                percorridos_str = f"{percorridos:,} km".replace(',', ' ')
        
        print(f"📊 Percorridos: {percorridos_str}")
        
        checkout_fuel_level = inspection_data.get('fuel_level') or 'R'
        print(f"🟡 Check-out fuel: {checkout_fuel_level}")
    else:
        # Para check-in, usar dados normais
        odometer = inspection_data.get('odometer_reading', 'N/A')
        if odometer and odometer != 'N/A':
            try:
                odometer_str = f"{int(odometer):,} km".replace(',', ' ')
            except (ValueError, TypeError):
                odometer_str = f"{odometer} km"
        else:
            odometer_str = 'N/A'
        
        fuel_level = inspection_data.get('fuel_level') or 'R'
        checkout_odometer_str = 'N/A'
        checkout_fuel_level = 'R'
        percorridos_str = 'N/A'
    
    print(f"⛽ Raw fuel_level (check-in): '{fuel_level}' (type: {type(fuel_level)})")
    
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
    print(f"✅ Converted fuel_level (check-in): '{fuel_level}'")
    fuel_percent = fuel_to_percent(fuel_level)
    print(f"📊 Fuel percent (check-in): {fuel_percent}%")
    
    # Process checkout fuel if checkout
    if is_checkout:
        print(f"⛽ Raw checkout_fuel_level: '{checkout_fuel_level}' (type: {type(checkout_fuel_level)})")
        
        if isinstance(checkout_fuel_level, str) and checkout_fuel_level.strip().replace('.', '', 1).isdigit():
            try:
                checkout_fuel_level = float(checkout_fuel_level) if '.' in checkout_fuel_level else int(checkout_fuel_level)
            except (ValueError, TypeError):
                pass
        
        if isinstance(checkout_fuel_level, (int, float)):
            if checkout_fuel_level == 0:
                checkout_fuel_level = 'R'
            elif checkout_fuel_level <= 12.5:
                checkout_fuel_level = '1/8'
            elif checkout_fuel_level <= 25:
                checkout_fuel_level = '1/4'
            elif checkout_fuel_level <= 37.5:
                checkout_fuel_level = '3/8'
            elif checkout_fuel_level <= 50:
                checkout_fuel_level = '1/2'
            elif checkout_fuel_level <= 62.5:
                checkout_fuel_level = '5/8'
            elif checkout_fuel_level <= 75:
                checkout_fuel_level = '3/4'
            elif checkout_fuel_level <= 87.5:
                checkout_fuel_level = '7/8'
            else:
                checkout_fuel_level = 'F'
        print(f"✅ Converted checkout_fuel_level: '{checkout_fuel_level}'")
        checkout_fuel_percent = fuel_to_percent(checkout_fuel_level)
        print(f"📊 Checkout fuel percent: {checkout_fuel_percent}%")
    else:
        checkout_fuel_percent = 0
    
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
        
        # Determine status based on inspection type
        inspection_type = inspection_data.get('inspection_type', '')
        if inspection_type in ['checkout', 'self_checkout']:
            status_text = "Concluído"
            status_color = HexColor('#10b981')  # Green
        else:
            status_text = "Pendente"
            status_color = HexColor('#f59e0b')  # Orange
        
        c.setFillColor(status_color)
        c.drawRightString(value_x, content_y, status_text)
    
    y_pos -= box_height + 15
    
    # Croqui de Danos e Informações da Entrega (side by side)
    if inspection_data.get('damage_croqui'):
        try:
            croqui_data = inspection_data['damage_croqui']
            
            # Handle PostgreSQL HEX format (\x...)
            if isinstance(croqui_data, (bytes, memoryview)):
                # Already bytes - use directly
                img_data = bytes(croqui_data)
            elif isinstance(croqui_data, str):
                if croqui_data.startswith('\\x'):
                    # PostgreSQL HEX format - convert to bytes
                    import binascii
                    hex_data = croqui_data[2:]  # Remove \x prefix
                    img_data = binascii.unhexlify(hex_data)
                elif croqui_data.startswith('data:image'):
                    # Data URL format - extract base64
                    croqui_data = croqui_data.split(',')[1]
                    # Clean base64: remove ALL invalid characters (keep only A-Z, a-z, 0-9, +, /, =)
                    import re
                    croqui_data = re.sub(r'[^A-Za-z0-9+/=]', '', croqui_data)
                    # Remove existing padding to recalculate
                    croqui_data = croqui_data.rstrip('=')
                    # Fix base64 padding
                    padding_needed = (4 - len(croqui_data) % 4) % 4
                    if padding_needed:
                        croqui_data += '=' * padding_needed
                    img_data = base64.b64decode(croqui_data)
                else:
                    # Raw base64 - fix padding and decode
                    croqui_data = croqui_data.strip().replace('\n', '').replace('\r', '').replace(' ', '')
                    padding_needed = (4 - len(croqui_data) % 4) % 4
                    if padding_needed:
                        croqui_data += '=' * padding_needed
                    img_data = base64.b64decode(croqui_data)
            else:
                raise ValueError(f"Unsupported croqui_data type: {type(croqui_data)}")
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
            
            # Caixa azul - duas colunas: Combustível (esquerda) e Quilómetros (direita)
            content_y = y_pos - 18
            
            # Coluna esquerda - Combustível (centralizada)
            left_col_width = left_box_width / 2
            left_col_center = 40 + left_col_width / 2
            
            c.setFont("Helvetica-Bold", 9)
            c.setFillColor(HexColor('#009cb6'))
            c.drawCentredString(left_col_center, content_y, "Combustível:")
            
            content_y_fuel = content_y - 15
            
            # Barra Entrega
            bar_width_small = left_col_width * 0.85
            bar_left = left_col_center - bar_width_small / 2
            bar_height_small = 12
            
            c.setFont("Helvetica-Bold", 7)
            c.setFillColor(HexColor('#009cb6'))
            c.drawCentredString(left_col_center, content_y_fuel, "Entrega")
            
            content_y_fuel -= 12
            
            # Marcadores barra entrega
            c.setFont("Helvetica-Bold", 6)
            c.setFillColor(HexColor('#009cb6'))
            c.drawString(bar_left - 8, content_y_fuel, "R")
            c.drawCentredString(bar_left + bar_width_small * 0.25, content_y_fuel, "1/4")
            c.drawCentredString(bar_left + bar_width_small * 0.5, content_y_fuel, "1/2")
            c.drawCentredString(bar_left + bar_width_small * 0.75, content_y_fuel, "3/4")
            c.drawString(bar_left + bar_width_small + 5, content_y_fuel, "F")
            
            content_y_fuel -= 14
            
            # Barra entrega
            c.setStrokeColor(HexColor('#009cb6'))
            c.setLineWidth(1.5)
            c.setFillColor(HexColor('#ffffff'))
            c.roundRect(bar_left, content_y_fuel, bar_width_small, bar_height_small, 3, fill=1, stroke=1)
            
            if fuel_percent > 0:
                c.setFillColor(HexColor('#009cb6'))
                fill_width = max(6, (bar_width_small - 3) * (fuel_percent / 100))
                c.roundRect(bar_left + 1.5, content_y_fuel + 1.5, fill_width, bar_height_small - 3, 2, fill=1, stroke=0)
            
            c.setStrokeColor(HexColor('#009cb6'))
            c.setLineWidth(0.5)
            for pos in [0, 0.25, 0.5, 0.75, 1.0]:
                x = bar_left + bar_width_small * pos
                c.line(x, content_y_fuel + 2, x, content_y_fuel + bar_height_small - 2)
            
            content_y_fuel -= 18
            
            # Barra Recolha
            c.setFont("Helvetica-Bold", 7)
            c.setFillColor(HexColor('#009cb6'))
            c.drawCentredString(left_col_center, content_y_fuel, "Recolha")
            
            content_y_fuel -= 12
            
            # Marcadores barra recolha
            c.setFont("Helvetica-Bold", 6)
            c.setFillColor(HexColor('#009cb6'))
            c.drawString(bar_left - 8, content_y_fuel, "R")
            c.drawCentredString(bar_left + bar_width_small * 0.25, content_y_fuel, "1/4")
            c.drawCentredString(bar_left + bar_width_small * 0.5, content_y_fuel, "1/2")
            c.drawCentredString(bar_left + bar_width_small * 0.75, content_y_fuel, "3/4")
            c.drawString(bar_left + bar_width_small + 5, content_y_fuel, "F")
            
            content_y_fuel -= 14
            
            # Barra recolha
            c.setStrokeColor(HexColor('#009cb6'))
            c.setLineWidth(1.5)
            c.setFillColor(HexColor('#ffffff'))
            c.roundRect(bar_left, content_y_fuel, bar_width_small, bar_height_small, 3, fill=1, stroke=1)
            
            if checkout_fuel_percent > 0:
                c.setFillColor(HexColor('#009cb6'))
                fill_width = max(6, (bar_width_small - 3) * (checkout_fuel_percent / 100))
                c.roundRect(bar_left + 1.5, content_y_fuel + 1.5, fill_width, bar_height_small - 3, 2, fill=1, stroke=0)
            
            c.setStrokeColor(HexColor('#009cb6'))
            c.setLineWidth(0.5)
            for pos in [0, 0.25, 0.5, 0.75, 1.0]:
                x = bar_left + bar_width_small * pos
                c.line(x, content_y_fuel + 2, x, content_y_fuel + bar_height_small - 2)
            
            # Coluna direita - Quilómetros (centralizada)
            right_col_center = 40 + left_col_width + (left_col_width / 2)
            
            c.setFont("Helvetica-Bold", 9)
            c.setFillColor(HexColor('#009cb6'))
            c.drawCentredString(right_col_center, content_y, "Quilómetros:")
            
            content_y_km = content_y - 15
            
            # Entrega
            c.setFont("Helvetica-Bold", 7)
            c.setFillColor(HexColor('#009cb6'))
            c.drawCentredString(right_col_center, content_y_km, "Entrega")
            
            content_y_km -= 12
            
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(HexColor('#111827'))
            c.drawCentredString(right_col_center, content_y_km, odometer_str)
            
            content_y_km -= 20
            
            # Recolha
            c.setFont("Helvetica-Bold", 7)
            c.setFillColor(HexColor('#009cb6'))
            c.drawCentredString(right_col_center, content_y_km, "Recolha")
            
            content_y_km -= 12
            
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(HexColor('#111827'))
            c.drawCentredString(right_col_center, content_y_km, checkout_odometer_str)
            
            content_y_km -= 20
            
            # Percorridos
            c.setFont("Helvetica-Bold", 7)
            c.setFillColor(HexColor('#009cb6'))
            c.drawCentredString(right_col_center, content_y_km, "Percorridos")
            
            content_y_km -= 12
            
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(HexColor('#111827'))
            c.drawCentredString(right_col_center, content_y_km, percorridos_str)
            
            # Right box - SEMPRE caixa branca com croqui
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
    
    # Photos grid - CONDITIONAL LOGIC for checkout (recolha)
    all_photos = inspection_data.get('photos', [])
    
    # IMMEDIATE LOGGING
    logging.info(f"📸 PDF GENERATOR STARTED - Type: {inspection_data.get('inspection_type')}")
    logging.info(f"📸 PDF GENERATOR - photos count: {len(all_photos)}")
    logging.info(f"📸 PDF GENERATOR - checkin_photos count: {len(inspection_data.get('checkin_photos', []))}")
    
    # Separate damage photos from normal inspection photos
    damage_photos = [p for p in all_photos if p.get('photo_type', '').startswith('damage_') and p.get('photo_type') != 'damage_croqui']
    normal_photos = [p for p in all_photos if not p.get('photo_type', '').startswith('damage_') and p.get('photo_type') != 'damage_croqui' and p.get('photo_type') != 'signature']
    
    # Get checkin photos if this is a checkout and we need them
    checkin_photos = inspection_data.get('checkin_photos', [])
    
    # Determine which photos to show based on scenario
    photos_to_show = []
    
    if inspection_data['inspection_type'] == 'checkout':
        # CHECKOUT (RECOLHA) - Apply conditional logic
        has_damage_photos = len(damage_photos) > 0
        has_normal_photos = len(normal_photos) > 0
        has_checkin_photos = len(checkin_photos) > 0
        
        logging.info(f"📸 PDF Photos - damage: {len(damage_photos)}, normal: {len(normal_photos)}, checkin: {len(checkin_photos)}")
        logging.info(f"📸 All photos types: {[p.get('photo_type') for p in all_photos]}")
        logging.info(f"📸 Checkin photos types: {[p.get('photo_type') for p in checkin_photos]}")
        
        # Scenario 1: No new photos in checkout -> show checkin photos
        if not has_normal_photos and not has_damage_photos:
            if has_checkin_photos:
                photos_to_show = [{'photos': checkin_photos, 'title': 'Fotografias da Entrega'}]
                logging.info(f"📸 Scenario 1: Showing {len(checkin_photos)} checkin photos")
            else:
                logging.warning("📸 No photos available for checkout PDF")
        
        # Scenario 2: Only new normal photos -> show only checkout normal photos
        elif has_normal_photos and not has_damage_photos:
            photos_to_show = [{'photos': normal_photos, 'title': 'Fotografias da Recolha'}]
            logging.info(f"📸 Scenario 2: Showing {len(normal_photos)} normal checkout photos")
        
        # Scenario 3: New normal photos + damage photos -> show damage first, then normal
        elif has_normal_photos and has_damage_photos:
            photos_to_show = [
                {'photos': damage_photos, 'title': 'Fotografias dos Danos (Recolha)'},
                {'photos': normal_photos, 'title': 'Fotografias da Recolha'}
            ]
            logging.info(f"📸 Scenario 3: Showing {len(damage_photos)} damage + {len(normal_photos)} normal photos")
        
        # Scenario 4: Only damage photos -> show damage + checkin photos
        elif has_damage_photos and not has_normal_photos:
            if has_checkin_photos:
                photos_to_show = [
                    {'photos': damage_photos, 'title': 'Fotografias dos Danos (Recolha)'},
                    {'photos': checkin_photos, 'title': 'Fotografias da Entrega'}
                ]
                logging.info(f"📸 Scenario 4: Showing {len(damage_photos)} damage + {len(checkin_photos)} checkin photos")
            else:
                photos_to_show = [{'photos': damage_photos, 'title': 'Fotografias dos Danos (Recolha)'}]
                logging.info(f"📸 Scenario 5: Showing {len(damage_photos)} damage photos only")
    else:
        # CHECKIN (ENTREGA) - Show all photos normally
        if all_photos:
            photos_to_show = [{'photos': all_photos, 'title': 'Fotografias da Inspeção'}]
    
    # Render photos sections
    if photos_to_show:
        # Photo labels for standard inspection photos
        photo_labels = [
            "Frente", "Frente Esquerda", "Lado Esquerdo",
            "Traseira Esquerda", "Traseira", "Traseira Direita",
            "Lado Direito", "Frente Direita", "Conta-Quilómetros"
        ]
        
        for section in photos_to_show:
            photos = section['photos']
            section_title = section['title']
            
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(HexColor('#1f2937'))
            c.drawString(40, y_pos, section_title)
            y_pos -= 15
            
            # Grid settings - same width as croqui box
            cols = 3
            grid_total_width = width - 80  # Same as croqui border_width
            spacing_horizontal = 10
            photo_width = (grid_total_width - spacing_horizontal * 2) / cols
            photo_height = photo_width * 0.6  # Smaller ratio
            spacing_vertical = 15  # Increased vertical spacing
            
            x_start = 40
            y_start = y_pos
            
            logging.info(f"🚨 PDF GENERATOR VERSION: 2026-04-20 09:58 - HEX FORMAT SUPPORT ACTIVE")
            
            for idx, photo in enumerate(photos[:9]):
                if idx > 0 and idx % cols == 0:
                    y_start -= photo_height + spacing_vertical + 8
                
                col = idx % cols
                x = x_start + col * (photo_width + spacing_horizontal)
                y = y_start - photo_height
                
                try:
                    photo_data = photo['image_data']
                    
                    # Log data type for debugging
                    logging.info(f"📸 Processing photo {idx} ({photo.get('photo_type', 'unknown')}): type={type(photo_data).__name__}, len={len(photo_data) if hasattr(photo_data, '__len__') else 'N/A'}")
                    
                    # Handle PostgreSQL HEX format (\x...)
                    if isinstance(photo_data, (bytes, memoryview)):
                        # Already bytes - use directly
                        img_data = bytes(photo_data)
                    elif isinstance(photo_data, str):
                        if photo_data.startswith('\\x'):
                            # PostgreSQL HEX format - convert to bytes
                            import binascii
                            hex_data = photo_data[2:]  # Remove \x prefix
                            img_data = binascii.unhexlify(hex_data)
                        elif photo_data.startswith('data:image'):
                            # Data URL format - extract base64
                            photo_data = photo_data.split(',')[1]
                            # Clean base64: remove ALL invalid characters (keep only A-Z, a-z, 0-9, +, /, =)
                            import re
                            photo_data = re.sub(r'[^A-Za-z0-9+/=]', '', photo_data)
                            # Remove existing padding to recalculate
                            photo_data = photo_data.rstrip('=')
                            # Fix base64 padding
                            padding_needed = (4 - len(photo_data) % 4) % 4
                            if padding_needed:
                                photo_data += '=' * padding_needed
                            img_data = base64.b64decode(photo_data)
                        else:
                            # Raw base64 - fix padding and decode
                            photo_data = photo_data.strip().replace('\n', '').replace('\r', '').replace(' ', '')
                            padding_needed = (4 - len(photo_data) % 4) % 4
                            if padding_needed:
                                photo_data += '=' * padding_needed
                            img_data = base64.b64decode(photo_data)
                    else:
                        raise ValueError(f"Unsupported image_data type: {type(photo_data)}")
                    img = Image.open(io.BytesIO(img_data))
                    
                    # Convert to RGB if needed
                    if img.mode == 'RGBA':
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        background.paste(img, mask=img.split()[3])
                        img = background
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # Calculate target size in pixels for the photo box
                    target_width_px = int(photo_width * 2)  # 2x for better quality
                    target_height_px = int(photo_height * 2)
                    
                    # Calculate cover fit dimensions
                    img_width, img_height = img.size
                    img_aspect = img_width / img_height
                    photo_aspect = target_width_px / target_height_px
                    
                    if img_aspect > photo_aspect:
                        # Image is wider - fit to height and crop width
                        new_height = target_height_px
                        new_width = int(new_height * img_aspect)
                        crop_x = (new_width - target_width_px) // 2
                        crop_y = 0
                    else:
                        # Image is taller - fit to width and crop height
                        new_width = target_width_px
                        new_height = int(new_width / img_aspect)
                        crop_x = 0
                        crop_y = (new_height - target_height_px) // 2
                    
                    # Resize image
                    img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    # Crop to exact size
                    img_cropped = img_resized.crop((crop_x, crop_y, crop_x + target_width_px, crop_y + target_height_px))
                    
                    # Create rounded corners mask
                    mask = Image.new('L', (target_width_px, target_height_px), 0)
                    draw = ImageDraw.Draw(mask)
                    radius_px = int(6 * 2)  # 2x for better quality
                    draw.rounded_rectangle([(0, 0), (target_width_px, target_height_px)], radius=radius_px, fill=255)
                    
                    # Apply mask
                    output = Image.new('RGB', (target_width_px, target_height_px), (255, 255, 255))
                    output.paste(img_cropped, (0, 0))
                    output.putalpha(mask)
                    
                    # Draw image
                    c.drawImage(ImageReader(output), x, y, width=photo_width, height=photo_height, mask='auto')
                    
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
