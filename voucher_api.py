from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from datetime import datetime
import psycopg2
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import io
from jinja2 import Template
import urllib.request

router = APIRouter()

class EmailRequest(BaseModel):
    email: str

DATABASE_URL = os.environ.get('DATABASE_URL')

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
            'vehicle_image': f'https://rentalprices.pt/static/vehicles/{result[13]}.jpg' if result[13] else ''
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
    """Generate and return voucher PDF"""
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
        
        print(f"[VOUCHER PRINT] Starting PDF generation with ReportLab")
        
        # Criar PDF com ReportLab
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Header
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, height - 50, f"VOUCHER {booking_data.get('voucher_number')}")
        
        # Informações do cliente
        p.setFont("Helvetica", 12)
        y_position = height - 100
        p.drawString(50, y_position, f"Cliente: {booking_data.get('client_name')}")
        y_position -= 20
        p.drawString(50, y_position, f"Email: {booking_data.get('client_email')}")
        y_position -= 20
        p.drawString(50, y_position, f"Telefone: {booking_data.get('client_phone')}")
        
        # Veículo
        y_position -= 40
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y_position, "Veículo:")
        y_position -= 20
        p.setFont("Helvetica", 12)
        p.drawString(50, y_position, f"{booking_data.get('vehicle_group')}")
        
        # Datas
        y_position -= 40
        p.drawString(50, y_position, f"Levantamento: {booking_data.get('pickup_date')} {booking_data.get('pickup_time')}")
        y_position -= 20
        p.drawString(50, y_position, f"Entrega: {booking_data.get('dropoff_date')} {booking_data.get('dropoff_time')}")
        
        # Valores
        y_position -= 40
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y_position, "Valores:")
        y_position -= 20
        p.setFont("Helvetica", 12)
        p.drawString(50, y_position, f"Total: €{booking_data.get('total_price')}")
        y_position -= 20
        p.drawString(50, y_position, f"Depósito: €{booking_data.get('deposit')}")
        y_position -= 20
        p.drawString(50, y_position, f"A Pagar: €{booking_data.get('amount_to_pay')}")
        
        # Tentar adicionar imagem do veículo se existir
        if booking_data.get('vehicle_image'):
            try:
                print(f"[VOUCHER PRINT] Loading vehicle image: {booking_data.get('vehicle_image')}")
                img_data = urllib.request.urlopen(booking_data.get('vehicle_image'), timeout=10).read()
                img = ImageReader(io.BytesIO(img_data))
                p.drawImage(img, 400, height - 200, width=150, height=100)
                print(f"[VOUCHER PRINT] Vehicle image added")
            except Exception as e:
                print(f"[VOUCHER PRINT] Could not load vehicle image: {e}")
        
        p.showPage()
        p.save()
        
        pdf_file = buffer.getvalue()
        buffer.close()
        print(f"[VOUCHER PRINT] PDF generated successfully with ReportLab, size: {len(pdf_file)} bytes")
        
        # Return PDF
        return StreamingResponse(
            io.BytesIO(pdf_file),
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
        # Generate PDF with custom URL fetcher for images
        html_content = render_voucher_template(booking_data)
        
        import urllib.request
        import time
        def custom_url_fetcher(url):
            """Custom URL fetcher with longer timeout and retries for images"""
            print(f"[VOUCHER EMAIL] Fetching URL: {url}")
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    data = urllib.request.urlopen(url, timeout=60).read()
                    print(f"[VOUCHER EMAIL] Successfully loaded {url}, size: {len(data)} bytes")
                    return {'string': data, 'mime_type': 'image/png'}
                except Exception as e:
                    print(f"[VOUCHER EMAIL] Attempt {attempt + 1}/{max_retries} failed for {url}: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(2)
                    else:
                        raise Exception(f"Falha ao carregar imagem {url} após {max_retries} tentativas: {e}")
        
        pdf_file = HTML(string=html_content, url_fetcher=custom_url_fetcher).write_pdf()
        print(f"[VOUCHER EMAIL] PDF generated successfully, size: {len(pdf_file)} bytes")
        
        # Get Gmail OAuth credentials
        print(f"[VOUCHER EMAIL] Loading Gmail OAuth credentials")
        credentials = get_gmail_credentials()
        
        if not credentials:
            print(f"[VOUCHER EMAIL] Gmail OAuth not configured")
            raise HTTPException(status_code=500, detail='Gmail não está configurado. Vá a Admin Settings → Email e conecte o Gmail.')
        
        # Create email message
        msg = MIMEMultipart()
        msg['To'] = recipient_email
        msg['Subject'] = f'Voucher de Reserva - {booking_data["voucher_number"]}'
        
        # Email body
        email_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #009cb6;">Voucher de Reserva - AutoPrudente</h2>
                <p>Caro(a) {booking_data['client_name']},</p>
                <p>Segue em anexo o voucher da sua reserva.</p>
                
                <div style="background: #f9fafb; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #009cb6; margin-top: 0;">Detalhes da Reserva</h3>
                    <p><strong>Voucher:</strong> {booking_data['voucher_number']}</p>
                    <p><strong>Veículo:</strong> {booking_data['vehicle_group']}</p>
                    <p><strong>Levantamento:</strong> {booking_data['pickup_date']} às {booking_data['pickup_time']}</p>
                    <p><strong>Entrega:</strong> {booking_data['dropoff_date']} às {booking_data['dropoff_time']}</p>
                    <p><strong>Valor a Pagar no Levantamento:</strong> €{booking_data['amount_to_pay']}</p>
                </div>
                
                <p>Por favor, apresente este voucher no momento do levantamento da viatura.</p>
                
                <p>Para qualquer questão, não hesite em contactar-nos:</p>
                <p>
                    📞 +351 289 123 456<br>
                    📱 +351 912 345 678<br>
                    ✉️ info@autoprudente.pt
                </p>
                
                <p>Obrigado por escolher a AutoPrudente!</p>
                
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                <p style="font-size: 12px; color: #6b7280;">
                    Este é um email automático. Por favor, não responda a este email.
                </p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(email_body, 'html'))
        
        # Attach PDF
        print(f"[VOUCHER EMAIL] Attaching PDF to email")
        part = MIMEBase('application', 'pdf')
        part.set_payload(pdf_file)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="voucher_{booking_data["voucher_number"]}.pdf"')
        msg.attach(part)
        
        # Send via Gmail API
        print(f"[VOUCHER EMAIL] Sending email via Gmail API to {recipient_email}")
        try:
            service = build('gmail', 'v1', credentials=credentials)
            raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode()
            message_body = {'raw': raw_message}
            
            sent_message = service.users().messages().send(userId='me', body=message_body).execute()
            print(f"[VOUCHER EMAIL] Email sent successfully! Message ID: {sent_message['id']}")
            
        except Exception as gmail_error:
            print(f"[VOUCHER EMAIL] Gmail API error: {gmail_error}")
            raise HTTPException(status_code=500, detail=f'Erro ao enviar email: {str(gmail_error)}')
        
        return {'ok': True, 'message': 'Voucher enviado com sucesso'}
        
    except HTTPException as he:
        print(f"[VOUCHER EMAIL] HTTP Exception: {he.detail}")
        raise
    except Exception as e:
        print(f"[VOUCHER EMAIL] Error sending voucher email: {e}")
        import traceback
        traceback.print_exc()
        error_msg = str(e)
        if 'Authentication' in error_msg or 'login' in error_msg.lower():
            error_msg = 'Erro de autenticação SMTP. Contacte o administrador.'
        elif 'Connection' in error_msg or 'timeout' in error_msg.lower():
            error_msg = 'Erro de conexão ao servidor de email. Tente novamente.'
        raise HTTPException(status_code=500, detail=error_msg)
