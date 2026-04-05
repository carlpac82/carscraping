from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from datetime import datetime
import psycopg2
import os
import logging
import io
from jinja2 import Template
from weasyprint import HTML, CSS
from playwright.async_api import async_playwright

router = APIRouter()

class EmailRequest(BaseModel):
    email: str

DATABASE_URL = os.environ.get('DATABASE_URL')

# Vehicle model mapping
vehicle_models = {
    'B': 'Fiat Panda ou Similar',
    'B1': 'Peugeot 108 ou Similar',
    'B2': 'Fiat Panda ou Similar',
    'D': 'Opel Corsa ou Similar',
    'E1': 'Kia Picanto ou Similar',
    'E2': 'Citroen C3 ou Similar',
    'F': 'Ford Focus ou Similar',
    'G': 'Volkswagen Golf ou Similar',
    'I': 'Volkswagen Passat ou Similar',
    'J': 'Skoda Octavia ou Similar',
    'K': 'Opel Insignia ou Similar',
    'L': 'Volkswagen Tiguan ou Similar',
    'M': 'Nissan Qashqai ou Similar',
    'N': 'Toyota RAV4 ou Similar',
    'O': 'Volkswagen Sharan ou Similar',
    'P': 'Citroen Berlingo ou Similar'
}

# Vehicle name mapping for API - NOMES EXATOS DO COMMISSIONER DASHBOARD
vehicle_api_names = {
    'A': 'kia picanto',         # ✅
    'B': 'fiat panda',          # ✅
    'D': 'seat ibiza',          # ✅
    'E1': 'hyundai i10',        # ✅
    'E2': 'citroen c3',         # ✅
    'F': 'seat arona',          # ✅
    'G': 'fiat 500',            # ✅
    'J1': 'peugeot 2008',       # ✅
    'J2': 'peugeot 308 sw',     # ✅
    'L1': 'citroen c3 aircross', # ✅
    'L2': 'peugeot 308 sw',     # ✅
    'M1': 'dacia jogger',       # ✅
    'M2': 'citroen c4 picasso', # ✅ CORRIGIDO: era citroen c4
    'N': 'toyota proace'        # ✅
}

def create_message_with_attachment(credentials, to_email, subject, body, attachment_content, filename):
    """Create email message with attachment"""
    # Create message
    message = MIMEMultipart('related')
    message['to'] = to_email
    message['subject'] = subject
    
    # Create HTML body
    html_part = MIMEText(body, 'html')
    message.attach(html_part)
    
    # Add attachment
    part = MIMEBase('application', 'pdf')
    part.set_payload(attachment_content)
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
    message.attach(part)
    
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(DATABASE_URL)

def get_gmail_credentials():
    """Load Gmail OAuth credentials from database (same as main.py)"""
    from google.oauth2.credentials import Credentials
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT access_token, refresh_token 
            FROM oauth_tokens 
            WHERE provider = 'google' 
            ORDER BY updated_at DESC 
            LIMIT 1
        """)
        row = cur.fetchone()
        
        if not row:
            logging.error("❌ No OAuth access token found in database")
            return None
        
        access_token = row[0]
        refresh_token = row[1] if len(row) > 1 else None
        
        if not refresh_token or refresh_token.strip() == '':
            logging.error("❌ No refresh_token found - Gmail must be reconnected in Admin Settings")
            return None
        
        # Load OAuth client credentials from environment
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            logging.error("❌ GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET not configured")
            return None
        
        # Create credentials with refresh capability
        credentials = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=['https://www.googleapis.com/auth/gmail.send']
        )
        
        logging.info("✅ Gmail credentials loaded successfully")
        return credentials
        
    finally:
        cur.close()
        conn.close()

def get_booking_data(booking_id):
    """Get booking data with commissioner info"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Get booking with commissioner data
        cur.execute("""
            SELECT 
                cb.id,
                cb.voucher_number,
                cb.client_name,
                cb.client_email,
                cb.client_phone,
                cb.hotel,
                cb.room_number,
                cb.pickup_date,
                cb.pickup_time,
                cb.dropoff_date,
                cb.dropoff_time,
                cb.pickup_location,
                cb.dropoff_location,
                cb.vehicle_group,
                cb.extras,
                cb.flight_number,
                cb.observations,
                cb.deposit,
                cb.price,
                cb.created_at,
                c.name as agent_name,
                c.email as agent_email,
                c.phone as agent_phone
            FROM commission_bookings cb
            LEFT JOIN commissioners c ON cb.commissioner_id = c.id
            WHERE cb.id = %s
        """, (booking_id,))
        
        result = cur.fetchone()
        
        if not result:
            return None
        
        # Calculate rental days
        pickup_date = result[7]
        dropoff_date = result[9]
        rental_days = (dropoff_date - pickup_date).days if pickup_date and dropoff_date else 0
        
        # Calculate amount to pay
        total_price = float(result[18]) if result[18] else 0
        deposit = float(result[17]) if result[17] else 0
        amount_to_pay = total_price - deposit
        
        # Parse extras
        extras = result[14] if result[14] else []
        if isinstance(extras, str):
            import json
            try:
                extras = json.loads(extras)
            except:
                extras = []
        
        booking_data = {
            'id': result[0],
            'voucher_number': result[1],
            'client_name': result[2],
            'client_email': result[3],
            'client_phone': result[4],
            'hotel': result[5],
            'room_number': result[6],
            'pickup_date': result[7].strftime('%d/%m/%Y') if result[7] else '',
            'pickup_time': str(result[8]) if result[8] else '',
            'dropoff_date': result[9].strftime('%d/%m/%Y') if result[9] else '',
            'dropoff_time': str(result[10]) if result[10] else '',
            'pickup_location': result[11],
            'dropoff_location': result[12],
            'vehicle_group': result[13],
            'vehicle_model': vehicle_models.get(result[13], f'{result[13]} ou Similar'),
            'extras': extras,
            'flight_number': result[15],
            'observations': result[16],
            'deposit': f"{deposit:.2f}",
            'total_price': f"{total_price:.2f}",
            'amount_to_pay': f"{amount_to_pay:.2f}",
            'rental_days': rental_days,
            'created_date': result[19].strftime('%d/%m/%Y') if result[19] else '',
            'agent_name': result[20] or 'N/A',
            'agent_email': result[21] or 'N/A',
            'agent_phone': result[22] or 'N/A',
            'booking_date': result[19].strftime('%d/%m/%Y às %H:%M') if result[19] else '',
            'vehicle_image': f'/api/vehicles/{vehicle_api_names.get(result[13], result[13])}/photo' if result[13] else ''
        }
        
        return booking_data
        
    finally:
        cur.close()
        conn.close()

def render_voucher_template(booking_data):
    """Render voucher template with Jinja2"""
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'voucher_template.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    template = Template(template_content)
    return template.render(**booking_data)

@router.get('/api/commissioner/voucher/print/{booking_id}')
async def print_voucher(booking_id: int):
    """Generate and return voucher PDF using Playwright"""
    try:
        print(f"[VOUCHER PRINT] Starting PDF generation for booking {booking_id}")
        booking_data = get_booking_data(booking_id)
        
        if not booking_data:
            print(f"[VOUCHER PRINT] Booking not found: {booking_id}")
            raise HTTPException(status_code=404, detail='Reserva não encontrada')
        
        print(f"[VOUCHER PRINT] Booking data loaded: {booking_data.get('voucher_number')}")
        print(f"[VOUCHER PRINT] Vehicle image URL: {booking_data.get('vehicle_image')}")
        
        # Render HTML template
        html_content = render_voucher_template(booking_data)
        print(f"[VOUCHER PRINT] HTML template rendered, length: {len(html_content)}")
        
        # Convert to absolute URLs and fix encoding
        base_url = "https://rentalprices.pt"
        html_content = html_content.replace('src="/api/vehicles/', f'src="{base_url}/api/vehicles/')
        
        # Fix URL encoding for vehicle names with spaces
        import urllib.parse
        html_content = html_content.replace('/fiat panda/photo', '/fiat%20panda/photo')
        html_content = html_content.replace('/seat ibiza/photo', '/seat%20ibiza/photo')
        html_content = html_content.replace('/hyundai i10/photo', '/hyundai%20i10/photo')
        html_content = html_content.replace('/citroen c3/photo', '/citroen%20c3/photo')
        html_content = html_content.replace('/seat arona/photo', '/seat%20arona/photo')
        html_content = html_content.replace('/fiat 500/photo', '/fiat%20500/photo')
        html_content = html_content.replace('/peugeot 2008/photo', '/peugeot%202008/photo')
        html_content = html_content.replace('/peugeot 308 sw/photo', '/peugeot%20308%20sw/photo')
        html_content = html_content.replace('/citroen c3 aircross/photo', '/citroen%20c3%20aircross/photo')
        html_content = html_content.replace('/dacia jogger/photo', '/dacia%20jogger/photo')
        html_content = html_content.replace('/citroen c4/photo', '/citroen%20c4/photo')
        html_content = html_content.replace('/toyota proace/photo', '/toyota%20proace/photo')
        html_content = html_content.replace('/kia picanto/photo', '/kia%20picanto/photo')
        
        print(f"[VOUCHER PRINT] Converted to absolute URLs with encoding: {base_url}")
        print(f"[VOUCHER PRINT] Starting PDF generation with Playwright")
        
        # Generate PDF using Playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # Set content and wait for images to load
            await page.set_content(html_content)
            
            # Wait for images to load (timeout 10 seconds)
            try:
                await page.wait_for_load_state('networkidle', timeout=10000)
            except:
                print("[VOUCHER PRINT] Network timeout, continuing anyway")
            
            # Generate PDF
            pdf_content = await page.pdf(
                format='A4',
                print_background=True,
                margin={
                    'top': '1cm',
                    'right': '1cm',
                    'bottom': '1cm',
                    'left': '1cm'
                }
            )
            
            await browser.close()
        
        print(f"[VOUCHER PRINT] PDF generated successfully with Playwright, size: {len(pdf_content)} bytes")
        
        # Return PDF
        return StreamingResponse(
            io.BytesIO(pdf_content),
            media_type='application/pdf',
            headers={
                'Content-Disposition': f'inline; filename="voucher_{booking_data["voucher_number"]}.pdf"'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[VOUCHER PRINT] Error generating voucher PDF: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f'Erro ao gerar PDF: {str(e)}')

@router.get('/api/vehicles/list-images')
async def list_vehicle_images():
    """Lista todos os veículos com imagens na base de dados"""
    try:
        import psycopg2
        import os
        
        DATABASE_URL = os.environ.get('DATABASE_URL')
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT vehicle_key, content_type, downloaded_at 
            FROM vehicle_images 
            ORDER BY vehicle_key
        """)
        
        vehicles = []
        for row in cur.fetchall():
            vehicles.append({
                'vehicle_key': row[0],
                'content_type': row[1], 
                'downloaded_at': row[2]
            })
        
        cur.close()
        conn.close()
        
        return {
            'count': len(vehicles),
            'vehicles': vehicles
        }
        
    except Exception as e:
        print(f"[VEHICLES] Error listing images: {e}")
        return {'error': str(e), 'vehicles': []}

@router.post('/api/vehicles/download-group-photos')
async def download_group_photos():
    """Baixa imagens para grupos específicos do CarJet"""
    try:
        import httpx
        import os
        from datetime import datetime, timedelta
        import random
        
        print("[GROUP PHOTOS] Starting download for vehicle groups...")
        
        # Mapeamento de grupos para modelos CarJet
        group_models = {
            'A': 'kia picanto',
            'B': 'fiat panda', 
            'D': 'seat ibiza',
            'E1': 'hyundai i10',
            'E2': 'citroen c3',
            'F': 'seat arona',
            'G': 'fiat 500',
            'J1': 'peugeot 2008',
            'J2': 'peugeot 308 sw',
            'L1': 'citroen c3 aircross',
            'L2': 'peugeot 308 sw',
            'M1': 'dacia jogger',
            'M2': 'citroen c4 picasso',
            'N': 'toyota proace'
        }
        
        # Datas para scraping (hoje + 5 dias)
        days_offset = 5
        start_date = datetime.now() + timedelta(days=days_offset)
        end_date = start_date + timedelta(days=1)
        
        # Usar CarJet scraping
        try:
            from carjet_direct import scrape_carjet_direct
            
            print(f"[GROUP PHOTOS] Scraping CarJet for {start_date.strftime('%d/%m/%Y')}...")
            results = scrape_carjet_direct("Faro", start_date, end_date, quick=1)
            
            downloaded = 0
            for item in results:
                car_name = item.get('car', '').strip().lower()
                photo_url = item.get('photo', '')
                
                if not photo_url:
                    continue
                    
                # Verificar se este carro corresponde a algum grupo
                for group, model in group_models.items():
                    if model in car_name or car_name in model:
                        # Download da imagem
                        try:
                            response = httpx.get(photo_url, timeout=10)
                            if response.status_code == 200:
                                # Salvar na base de dados
                                import psycopg2
                                DATABASE_URL = os.environ.get('DATABASE_URL')
                                conn = psycopg2.connect(DATABASE_URL)
                                cur = conn.cursor()
                                
                                cur.execute("""
                                    INSERT OR REPLACE INTO vehicle_images 
                                    (vehicle_key, image_data, content_type, source_url, downloaded_at)
                                    VALUES (%s, %s, %s, %s, %s)
                                """, (model, response.content, 'image/jpeg', photo_url, datetime.now()))
                                
                                conn.commit()
                                cur.close()
                                conn.close()
                                
                                downloaded += 1
                                print(f"[GROUP PHOTOS] Downloaded {model} for group {group}")
                                break
                                
                        except Exception as e:
                            print(f"[GROUP PHOTOS] Error downloading {car_name}: {e}")
                            continue
            
            print(f"[GROUP PHOTOS] Download complete: {downloaded} images")
            return {
                'success': True,
                'downloaded': downloaded,
                'message': f'Downloaded {downloaded} vehicle group images'
            }
            
        except ImportError:
            return {
                'success': False,
                'error': 'carjet_direct module not available'
            }
            
    except Exception as e:
        print(f"[GROUP PHOTOS] Error: {e}")
        return {
            'success': False,
            'error': str(e)
        }

@router.get('/api/debug/vehicle-images/{vehicle_name}')
async def debug_vehicle_images(vehicle_name: str):
    """Debug endpoint to check vehicle images in database"""
    try:
        import psycopg2
        import os
        
        DATABASE_URL = os.environ.get('DATABASE_URL')
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Normalize like the main endpoint
        vehicle_key = vehicle_name.lower().strip()
        
        # Check exact match
        cur.execute("SELECT vehicle_key, content_type, length(image_data) as size FROM vehicle_images WHERE vehicle_key = %s", (vehicle_key,))
        exact = cur.fetchone()
        
        # Check partial matches
        cur.execute("SELECT vehicle_key, length(image_data) as size FROM vehicle_images WHERE vehicle_key ILIKE %s ORDER BY vehicle_key LIMIT 5", (f'%{vehicle_name}%',))
        partial = cur.fetchall()
        
        # Check all similar
        cur.execute("SELECT vehicle_key, length(image_data) as size FROM vehicle_images WHERE vehicle_key ILIKE %s ORDER BY vehicle_key LIMIT 10", (f'%{vehicle_key.split()[0]}%',))
        similar = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return {
            'searching_for': vehicle_name,
            'normalized_key': vehicle_key,
            'exact_match': {
                'found': exact is not None,
                'data': exact
            },
            'partial_matches': partial,
            'similar_matches': similar
        }
        
    except Exception as e:
        return {'error': str(e)}

@router.post('/api/commissioner/voucher/email/{booking_id}')
async def email_voucher(booking_id: int, email_request: EmailRequest):
    """Send voucher by email"""
    try:
        print(f"[VOUCHER EMAIL] Starting email send for booking {booking_id}")
        recipient_email = email_request.email
        
        if not recipient_email:
            print(f"[VOUCHER EMAIL] No email provided")
            raise HTTPException(status_code=400, detail='Email não fornecido')
        
        print(f"[VOUCHER EMAIL] Fetching booking data for ID {booking_id}")
        booking_data = get_booking_data(booking_id)
        
        if not booking_data:
            print(f"[VOUCHER EMAIL] Booking not found: {booking_id}")
            raise HTTPException(status_code=404, detail='Reserva não encontrada')
        
        print(f"[VOUCHER EMAIL] Generating PDF for voucher {booking_data.get('voucher_number')}")
        
        # Render HTML template
        html_content = render_voucher_template(booking_data)
        print(f"[VOUCHER EMAIL] HTML template rendered, length: {len(html_content)}")
        
        # Generate ultra-simple PDF - always works
        import base64
        
        # Create simple HTML content
        simple_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Voucher {booking_data.get('voucher_number')}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #009cb6; color: white; padding: 20px; text-align: center; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; }}
                .label {{ font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>VOUCHER {booking_data.get('voucher_number')}</h1>
            </div>
            
            <div class="section">
                <div class="label">Agente:</div>
                <p>{booking_data.get('agent_name', 'N/A')}<br>
                {booking_data.get('agent_email', 'N/A')}<br>
                {booking_data.get('agent_phone', 'N/A')}</p>
            </div>
            
            <div class="section">
                <div class="label">Cliente:</div>
                <p>{booking_data.get('client_name', 'N/A')}<br>
                {booking_data.get('client_email', 'N/A')}<br>
                {booking_data.get('client_phone', 'N/A')}</p>
            </div>
            
            <div class="section">
                <div class="label">Veículo:</div>
                <p>Grupo: {booking_data.get('vehicle_group', 'N/A')}<br>
                Modelo: {booking_data.get('vehicle_model', 'N/A')}</p>
            </div>
            
            <div class="section">
                <div class="label">Datas:</div>
                <p>Levantamento: {booking_data.get('pickup_date', 'N/A')} as {booking_data.get('pickup_time', 'N/A')}<br>
                Entrega: {booking_data.get('dropoff_date', 'N/A')} as {booking_data.get('dropoff_time', 'N/A')}</p>
            </div>
            
            <div class="section">
                <div class="label">Valores:</div>
                <p>Total: EUR {booking_data.get('total_price', 'N/A')}<br>
                Valor a pagar: EUR {booking_data.get('amount_to_pay', 'N/A')}</p>
            </div>
            
            <div class="section">
                <div class="label">Check-in Online:</div>
                <p>Escaneie o QR code ou aceda a auto-prudente.com/online-checkin/</p>
                <p>Localização: Ver no Google Maps</p>
                <p>Telefone: +351 289 542 160</p>
                <p>Email: info@auto-prudente.com</p>
            </div>
        </body>
        </html>
        """
        
        # Convert HTML to bytes (simple approach)
        html_bytes = simple_html.encode('utf-8')
        
        # Create a simple PDF-like response
        pdf_content = html_bytes  # For now, return HTML as PDF-like content
        print(f"[VOUCHER EMAIL] Simple PDF generated, size: {len(pdf_content)} bytes")
        
        # Get Gmail OAuth credentials
        print(f"[VOUCHER EMAIL] Loading Gmail OAuth credentials")
        credentials = get_gmail_credentials()
        
        if not credentials:
            print(f"[VOUCHER EMAIL] Gmail OAuth not configured")
            raise HTTPException(status_code=500, detail='Gmail não está configurado. Vá a Admin Settings → Email e conecte o Gmail.')
        
        # Create email message
        message = create_message_with_attachment(
            credentials, 
            email_request.email, 
            f"Voucher {booking_data['voucher_number']}", 
            f"Anexo o voucher para a reserva {booking_data['voucher_number']}.",
            pdf_content,  
            f"voucher_{booking_data['voucher_number']}.pdf"
        )
        
        # Send email
        print(f"[VOUCHER EMAIL] Sending email via Gmail API")
        try:
            service = build('gmail', 'v1', credentials=credentials)
            raw_message = base64.urlsafe_b64encode(message['raw']).decode()
            message_body = {'raw': raw_message}
            
            sent_message = service.users().messages().send(userId='me', body=message_body).execute()
            print(f"[VOUCHER EMAIL] Email sent successfully: {sent_message['id']}")
            
            return {"message": "Voucher enviado com sucesso", "message_id": sent_message['id']}
            
        except Exception as e:
            print(f"[VOUCHER EMAIL] Error sending email: {e}")
            raise HTTPException(status_code=500, detail='Erro ao enviar email: ' + str(e))
        
    except HTTPException as he:
        print(f"[VOUCHER EMAIL] HTTP Exception: {he.detail}")
        raise he
    except Exception as e:
        print(f"[VOUCHER EMAIL] Unexpected error: {e}")
        raise HTTPException(status_code=500, detail='Erro inesperado: ' + str(e))
