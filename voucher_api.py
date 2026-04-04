from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from datetime import datetime
import psycopg2
import os
from fpdf import FPDF
import io
from jinja2 import Template

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
        
        print(f"[VOUCHER PRINT] Starting PDF generation with fpdf2")
        
        # Generate PDF with fpdf2 - ultra fast, native Python
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Set font
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, f"VOUCHER {booking_data.get('voucher_number')}", 0, 1, "C")
        pdf.ln(10)
        
        # Client info
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "DADOS DO CLIENTE", 0, 1, "L")
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 6, f"Nome: {booking_data.get('client_name')}", 0, 1, "L")
        pdf.cell(0, 6, f"Email: {booking_data.get('client_email')}", 0, 1, "L")
        pdf.cell(0, 6, f"Telefone: {booking_data.get('client_phone')}", 0, 1, "L")
        pdf.ln(5)
        
        # Vehicle info
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "DADOS DO VEICULO", 0, 1, "L")
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 6, f"Grupo: {booking_data.get('vehicle_group')}", 0, 1, "L")
        pdf.cell(0, 6, f"Modelo: {booking_data.get('vehicle_model')}", 0, 1, "L")
        pdf.ln(5)
        
        # Dates
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "DATAS", 0, 1, "L")
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 6, f"Levantamento: {booking_data.get('pickup_date')} as {booking_data.get('pickup_time')}", 0, 1, "L")
        pdf.cell(0, 6, f"Entrega: {booking_data.get('dropoff_date')} as {booking_data.get('dropoff_time')}", 0, 1, "L")
        pdf.ln(5)
        
        # Values
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "VALORES", 0, 1, "L")
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 6, f"Total: EUR {booking_data.get('total_price')}", 0, 1, "L")
        pdf.cell(0, 6, f"Valor a pagar no levantamento: EUR {booking_data.get('amount_to_pay')}", 0, 1, "L")
        
        # Get PDF bytes
        pdf_content = pdf.output(dest='S').encode('latin-1')
        print(f"[VOUCHER PRINT] PDF generated with fpdf2, size: {len(pdf_content)} bytes")
        
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
        
        # Generate PDF with fpdf2 - ultra fast, native Python
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Set font
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, f"VOUCHER {booking_data.get('voucher_number')}", 0, 1, "C")
        pdf.ln(10)
        
        # Client info
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "DADOS DO CLIENTE", 0, 1, "L")
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 6, f"Nome: {booking_data.get('client_name')}", 0, 1, "L")
        pdf.cell(0, 6, f"Email: {booking_data.get('client_email')}", 0, 1, "L")
        pdf.cell(0, 6, f"Telefone: {booking_data.get('client_phone')}", 0, 1, "L")
        pdf.ln(5)
        
        # Vehicle info
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "DADOS DO VEICULO", 0, 1, "L")
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 6, f"Grupo: {booking_data.get('vehicle_group')}", 0, 1, "L")
        pdf.cell(0, 6, f"Modelo: {booking_data.get('vehicle_model')}", 0, 1, "L")
        pdf.ln(5)
        
        # Dates
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "DATAS", 0, 1, "L")
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 6, f"Levantamento: {booking_data.get('pickup_date')} as {booking_data.get('pickup_time')}", 0, 1, "L")
        pdf.cell(0, 6, f"Entrega: {booking_data.get('dropoff_date')} as {booking_data.get('dropoff_time')}", 0, 1, "L")
        pdf.ln(5)
        
        # Values
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "VALORES", 0, 1, "L")
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 6, f"Total: EUR {booking_data.get('total_price')}", 0, 1, "L")
        pdf.cell(0, 6, f"Valor a pagar no levantamento: EUR {booking_data.get('amount_to_pay')}", 0, 1, "L")
        
        # Get PDF bytes
        pdf_content = pdf.output(dest='S').encode('latin-1')
        print(f"[VOUCHER EMAIL] PDF generated with fpdf2, size: {len(pdf_content)} bytes")
        
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
