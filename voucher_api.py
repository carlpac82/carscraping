from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from datetime import datetime
import psycopg2
import os
from weasyprint import HTML
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import io
from jinja2 import Template

router = APIRouter()

class EmailRequest(BaseModel):
    email: str

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(DATABASE_URL)

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
        booking_data = get_booking_data(booking_id)
        
        if not booking_data:
            raise HTTPException(status_code=404, detail='Reserva não encontrada')
        
        # Render HTML template
        html_content = render_voucher_template(booking_data)
        
        # Generate PDF
        pdf_file = HTML(string=html_content).write_pdf()
        
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
        print(f"Error generating voucher PDF: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

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
        # Generate PDF
        html_content = render_voucher_template(booking_data)
        pdf_file = HTML(string=html_content).write_pdf()
        print(f"[VOUCHER EMAIL] PDF generated successfully, size: {len(pdf_file)} bytes")
        
        # Email configuration
        smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.environ.get('SMTP_PORT', 587))
        smtp_user = os.environ.get('SMTP_USER')
        smtp_password = os.environ.get('SMTP_PASSWORD')
        from_email = os.environ.get('FROM_EMAIL', smtp_user)
        
        print(f"[VOUCHER EMAIL] SMTP Config - Server: {smtp_server}, Port: {smtp_port}, User: {smtp_user[:5]}... (exists: {bool(smtp_user)})")
        
        if not smtp_user or not smtp_password:
            print(f"[VOUCHER EMAIL] SMTP credentials not configured")
            raise HTTPException(status_code=500, detail='Configuração de email não disponível. Contacte o administrador.')
        
        # Create email
        msg = MIMEMultipart()
        msg['From'] = from_email
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
        pdf_attachment = MIMEApplication(pdf_file, _subtype='pdf')
        pdf_attachment.add_header('Content-Disposition', 'attachment', 
                                 filename=f'voucher_{booking_data["voucher_number"]}.pdf')
        msg.attach(pdf_attachment)
        
        # Send email
        print(f"[VOUCHER EMAIL] Connecting to SMTP server {smtp_server}:{smtp_port}")
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            print(f"[VOUCHER EMAIL] Starting TLS")
            server.starttls()
            print(f"[VOUCHER EMAIL] Logging in with user {smtp_user}")
            server.login(smtp_user, smtp_password)
            print(f"[VOUCHER EMAIL] Sending email to {recipient_email}")
            server.send_message(msg)
        
        print(f"[VOUCHER EMAIL] Email sent successfully to {recipient_email}")
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
